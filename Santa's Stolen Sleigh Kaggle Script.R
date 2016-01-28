library(data.table)
library(ggplot2)
library(ggmap)

setwd('C:/Users/Rich/Google Drive/Kaggle/Santas Stolen Sleigh')
gifts <- read.csv('gifts.csv')
gifts <- as.data.table(gifts) 

north_pole = c(0, 90)
weight_limit = 1000
base_weight = 10
num_gifts = nrow(gifts)

#Exploratory Data Analysis
#Weight Distribution (Each Bin = 2 Unit Range eg 0-2)
ggplot(gifts, aes(Weight)) + geom_histogram(binwidth=2)

#Map of Gifts (Darker Color = Heavier Package)
ggplot() + borders("world") + geom_point(aes(x=gifts$Longitude, y=gifts$Latitude), alpha=gifts$Weight/max(gifts$Weight), size=0.0001)

#Number of Clusters
worst_case_trip = floor((weight_limit - base_weight)/max(gifts$Weight))
num_clusters = ceiling(num_gifts/worst_case_trip) 

#KMeans by Lat and Long
#clusters <- kmeans(gifts[,2:3, with=FALSE], num_clusters, iter.max = 100) #More iterations was slight improvement in score (13645393804.36600)
#gifts$Clusters <- clusters$cluster

#Kmeans by Long Only
clusters <- kmeans(gifts[,3, with=FALSE], num_clusters, iter.max = 100)
longs <- order(clusters$centers)
gifts$Clusters <- clusters$cluster

#Number of Gifts per Cluster
weight_per_cluster <- gifts[, sum(Weight), by=Clusters] #Highest weight is currently ~776, which is ok
weight_per_cluster <- weight_per_cluster[match(longs, weight_per_cluster$Clusters)]

#Combine consecutive clusters below weight limit
for (i in seq(1, num_clusters-1, 2)){
  if (weight_per_cluster$V1[i] + weight_per_cluster$V1[i+1] + base_weight < weight_limit){
    gifts$Clusters[gifts$Clusters == weight_per_cluster$Clusters[i]] <- weight_per_cluster$Clusters[i+1]
  }
}

longs2 <- longs[longs %in% gifts$Clusters]
weight_per_cluster2 <- gifts[, sum(Weight), by=Clusters] 
weight_per_cluster2 <- weight_per_cluster2[match(longs2, weight_per_cluster2$Clusters)]

for (i in seq(1, length(longs2)-1, 2)){
  if (weight_per_cluster2$V1[i] + weight_per_cluster2$V1[i+1] + base_weight < weight_limit){
    gifts$Clusters[gifts$Clusters == weight_per_cluster2$Clusters[i]] <- weight_per_cluster2$Clusters[i+1]
  }
}

longs3 <- longs2[longs2 %in% gifts$Clusters]
weight_per_cluster3 <- gifts[, sum(Weight), by=Clusters] 
weight_per_cluster3 <- weight_per_cluster3[match(longs3, weight_per_cluster3$Clusters)]

for (i in seq(1, length(longs3)-1, 2)){
  if (weight_per_cluster3$V1[i] + weight_per_cluster3$V1[i+1] + base_weight < weight_limit){
    gifts$Clusters[gifts$Clusters == weight_per_cluster3$Clusters[i]] <- weight_per_cluster3$Clusters[i+1]
  }
}

longs4 <- longs3[longs3 %in% gifts$Clusters]
weight_per_cluster4 <- gifts[, sum(Weight), by=Clusters] 
weight_per_cluster4 <- weight_per_cluster4[match(longs4, weight_per_cluster4$Clusters)]

for (i in seq(1, length(longs4)-1, 2)){
  if (weight_per_cluster4$V1[i] + weight_per_cluster4$V1[i+1] + base_weight < weight_limit){
    gifts$Clusters[gifts$Clusters == weight_per_cluster4$Clusters[i]] <- weight_per_cluster4$Clusters[i+1]
  }
}

longs5 <- longs4[longs4 %in% gifts$Clusters]
weight_per_cluster5 <- gifts[, sum(Weight), by=Clusters] 
weight_per_cluster5 <- weight_per_cluster5[match(longs5, weight_per_cluster5$Clusters)]

for (i in seq(1, length(longs5)-1, 2)){
  if (weight_per_cluster5$V1[i] + weight_per_cluster5$V1[i+1] + base_weight < weight_limit){
    gifts$Clusters[gifts$Clusters == weight_per_cluster5$Clusters[i]] <- weight_per_cluster5$Clusters[i+1]
  }
}

longs6 <- longs5[longs5 %in% gifts$Clusters]
weight_per_cluster6 <- gifts[, sum(Weight), by=Clusters] 
weight_per_cluster6 <- weight_per_cluster6[match(longs6, weight_per_cluster6$Clusters)]

for (i in seq(1, length(longs6)-1, 2)){
  if (weight_per_cluster6$V1[i] + weight_per_cluster6$V1[i+1] + base_weight < weight_limit){
    gifts$Clusters[gifts$Clusters == weight_per_cluster6$Clusters[i]] <- weight_per_cluster6$Clusters[i+1]
  }
}

longs7 <- longs6[longs6 %in% gifts$Clusters]
weight_per_cluster7 <- gifts[, sum(Weight), by=Clusters] 
weight_per_cluster7 <- weight_per_cluster7[match(longs7, weight_per_cluster7$Clusters)]

#Map Cluster Centroids
#cluster_centroids <- data.frame(clusters$centers)
#ggplot() + borders("world") + geom_point(aes(x=cluster_centroids$Longitude, y=0))

#Map Gifts Colored by Cluster
ggplot() + borders("world") + geom_point(aes(x=gifts$Longitude, y=gifts$Latitude), color=gifts$Clusters)

#Reorder Data to Deliver Items by Descending Latitude
submission <- setorder(gifts, -Latitude)
submission <- submission[, .(GiftId, Clusters)]
colnames(submission)[2] <- "TripId"

#Write CSV
setwd('C:/Users/Rich/Google Drive/Kaggle/Santas Stolen Sleigh')
write.csv(submission, 'santa_submission_long_only_collapsed.csv', row.names = FALSE)



