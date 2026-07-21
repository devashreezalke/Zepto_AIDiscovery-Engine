import os
import numpy as np
import logging
import matplotlib.pyplot as plt
from sklearn.cluster import DBSCAN
from sklearn.decomposition import PCA
from clustering.embeddings import generate_embeddings

logger = logging.getLogger(__name__)

def run_clustering(db_path='data/discovery.db', eps=0.45, min_samples=3):
    """Clusters document embeddings using DBSCAN and generates a 2D visualization."""
    doc_ids, embeddings = generate_embeddings(db_path)
    
    if len(doc_ids) == 0 or embeddings.size == 0:
        logger.warning("No embeddings to cluster. Run ingestion and analysis first.")
        return {}, []
        
    # 1. Normalize embeddings for Cosine distance equivalence via Euclidean distance
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    # Avoid divide by zero
    norms[norms == 0] = 1.0
    normalized_embeddings = embeddings / norms
    
    logger.info(f"Running DBSCAN clustering (eps={eps}, min_samples={min_samples})...")
    # DBSCAN clusters dense regions and flags outliers as -1
    dbscan = DBSCAN(eps=eps, min_samples=min_samples, metric='euclidean')
    cluster_labels = dbscan.fit_predict(normalized_embeddings)
    
    # Analyze clusters
    unique_labels = set(cluster_labels)
    n_clusters = len(unique_labels) - (1 if -1 in unique_labels else 0)
    noise_count = np.sum(cluster_labels == -1)
    noise_pct = (noise_count / len(cluster_labels)) * 100
    
    logger.info(f"Clustering complete. Identified {n_clusters} clusters.")
    logger.info(f"Noise documents: {noise_count} ({noise_pct:.1f}%)")
    
    # If noise is too high (e.g. >50%) or clusters is 0, we can adjust parameters dynamically
    # For now, we report the counts
    
    # 2. Project to 2D using PCA for visualization (highly robust, zero-compilation)
    logger.info("Projecting embeddings to 2D using PCA...")
    try:
        pca = PCA(n_components=2, random_state=42)
        coords_2d = pca.fit_transform(normalized_embeddings)
        
        # Plot and save to data/clusters.png
        plt.figure(figsize=(10, 8))
        
        # Plot noise
        noise_mask = (cluster_labels == -1)
        plt.scatter(
            coords_2d[noise_mask, 0], coords_2d[noise_mask, 1],
            c='#D1D5DB', label='Noise/Unclassified', alpha=0.5, s=25
        )
        
        # Plot active clusters
        for label in sorted(unique_labels):
            if label == -1:
                continue
            mask = (cluster_labels == label)
            plt.scatter(
                coords_2d[mask, 0], coords_2d[mask, 1],
                label=f'Theme Cluster {label}', alpha=0.8, s=40
            )
            
        plt.title('Zepto User Feedback Semantic Clusters (PCA Projection)', fontsize=14, fontweight='bold', pad=15)
        plt.xlabel('PCA Component 1')
        plt.ylabel('PCA Component 2')
        # Only show legend if there are not too many clusters
        if n_clusters < 15:
            plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        
        # Ensure output directory exists
        os.makedirs('data', exist_ok=True)
        img_path = os.path.join('data', 'clusters.png')
        plt.savefig(img_path, dpi=150)
        plt.close()
        logger.info(f"Cluster visualization saved successfully at {img_path}")
    except Exception as e:
        logger.error(f"Failed to generate cluster plot: {e}")

    # Create mapping of doc_id to cluster label
    doc_cluster_map = {doc_ids[i]: int(cluster_labels[i]) for i in range(len(doc_ids))}
    
    return doc_cluster_map, list(unique_labels)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    mapping, labels = run_clustering()
    print("Unique cluster labels:", labels)
