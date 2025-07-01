import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt


def predict_data(X,df):
    scaler = StandardScaler()
    print("called")
    X_scaled = scaler.fit_transform(X)

    # Cluster with KMeans (choose number of clusters)
    kmeans = KMeans(n_clusters=3, random_state=42)
    clusters = kmeans.fit_predict(X_scaled)

    # Add cluster labels back to df
    df['Cluster'] = clusters

    # Analyze clusters
    print(df.groupby('Cluster').mean())
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)

    plt.scatter(X_pca[:, 0], X_pca[:, 1], c=clusters, cmap='viridis')
    plt.title('KMeans Clusters Visualization')
    plt.xlabel('PCA1')
    plt.ylabel('PCA2')
    plt.show()




