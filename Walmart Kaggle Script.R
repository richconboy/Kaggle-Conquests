library(reshape2)
library(data.table)
library(randomForest)
library(Matrix)


#Read in Data
training_data <- read.csv('C:/Users/Rich/OneDrive/Documents/Independent Projects/Kaggle/Walmart/train.csv')
setDT(training_data)

test_data <-read.csv('C:/Users/Rich/OneDrive/Documents/Independent Projects/Kaggle/Walmart/test.csv')
setDT(test_data)


#Remove Symbols from Data (These will become column names)
clean <- function(dataVector){
  dataVector <- gsub(" ", "_", dataVector)
  dataVector <- gsub("-", "_", dataVector)
  dataVector <- gsub("&", "N", dataVector)
  dataVector <- gsub(",", "", dataVector)
  dataVector <- gsub(",", "", dataVector)
  dataVector <- gsub("/", "_", dataVector)
  return(dataVector)
}
training_data$DepartmentDescription <- clean(training_data$DepartmentDescription)
test_data$DepartmentDescription <-clean(test_data$DepartmentDescription)


#Cast to Wide Form and split out
cast_and_split <- function(dataset){
  dept_purchases <- dcast(data=dataset, VisitNumber ~ DepartmentDescription, value.var = 'ScanCount', subset= (ScanCount>0), fun.aggregate = sum)
  for(i in 2:length(names(dept_purchases))){
    names(dept_purchases)[i] <- paste("PUR", names(dept_purchases)[i], sep="_")
  }
  
  dept_returns <- dcast(data=dataset, VisitNumber ~ DepartmentDescription, value.var = 'ScanCount', subset= (ScanCount<0), fun.aggregate = sum)
  for(i in 2:length(names(dept_returns))){
    names(dept_returns)[i] <- paste("RET", names(dept_returns)[i], sep="_")
  }
  
  #fineline_purchases <- dcast(data=dataset, VisitNumber ~ FinelineNumber, value.var = 'ScanCount', subset= (ScanCount>0), fun.aggregate = sum)
  #for(i in 2:length(names(fineline_purchases))){
  #  names(fineline_purchases)[i] <- paste("PUR", names(fineline_purchases)[i], sep="_")
  #}
   
  #fineline_returns <- dcast(data=dataset, VisitNumber ~ FinelineNumber, value.var = 'ScanCount', subset= (ScanCount<0), fun.aggregate = sum)
  #for(i in 2:length(names(fineline_returns))){
  #  names(fineline_returns)[i] <- paste("RET", names(fineline_returns)[i], sep="_")
  #}
  
  weekdays <- unique(dataset[,.(VisitNumber, Weekday)], by='VisitNumber')
  weekdays$Dummy <- 1
  weekdays <- dcast(data=weekdays, VisitNumber ~ Weekday, value.var='Dummy')
  for(i in 2:length(names(weekdays))){
    names(weekdays)[i] <- paste("DAY", names(weekdays)[i], sep="_")
  }
   
  transactions <- merge(x=dept_purchases, y=dept_returns, by='VisitNumber', all.x=TRUE, all.y=TRUE)
  #transactions <- merge(x=transactions, y=fineline_purchases, by='VisitNumber', all.x=TRUE, all.y=TRUE)
  #transactions <- merge(x=transactions, y=fineline_returns, by='VisitNumber', all.x=TRUE, all.y=TRUE)
  transactions <- merge(x=transactions, y=weekdays, by='VisitNumber', all.x=TRUE, all.y=TRUE)
  
  transactions[is.na(transactions)] <- 0
  return(transactions)
}

model_train <- cast_and_split(training_data)
model_train <- merge(x=model_train, y=unique(training_data[,.(VisitNumber, TripType)]), by='VisitNumber', all.x=TRUE, all.y=TRUE)  

model_test <- cast_and_split(test_data)


#Specify number of levels
numberOfClasses <- length(unique(model_train$TripType))


#Remove useless predictors
train_label <- as.numeric(as.factor(model_train$TripType))-1
model_train[,VisitNumber:=NULL]
model_train[,TripType:=NULL]
test_label <- model_test$VisitNumber
model_test[,VisitNumber:=NULL]


#Subset columns from training data not in test data
model_train <- model_train[,names(model_train) %in% names(model_test), with=FALSE]
model_test <- model_test[,names(model_test) %in% names(model_train), with=FALSE]

trainMatrix <- model_train[,lapply(.SD,as.numeric)] %>% as.matrix
testMatrix <- model_train[,lapply(.SD, as.numeric)] %>% as.matrix


################## MODELING ##################
#XGBoost
#Sets Parameters
param <- list("objective" = "multi:softprob",
              "eval_metric" = "mlogloss",
              "num_class" = numberOfClasses)

#Cross-Validation
boost <- xgb.cv(param=param, data = trainMatrix, label = train_label, 
       nfold = 3, nrounds = 20)

#Fit Gradient Boost Model
boost <- xgboost(data = trainMatrix, param=param, label = train_label, nrounds = 50)
model <- dimnames(trainMatrix)[[2]]
importance_matrix <- xgb.importance(model, model = boost)
xgb.plot.importance(importance_matrix[1:10,])
xgb.plot.tree(feature_names = model, model = boost, n_first_tree = 2)


################# TEST #######################
#Make Predictions!
test_predictions <- matrix(predict(boost, testMatrix), ncol=numberOfClasses, byrow=TRUE)
submission <- data.frame(VisitNumber = test_label, test_predictions)
for(i in 2:length(names(submission))){
  names(submission)[i] <- gsub('X', 'TripType_', names(submission)[i])
}
names(submission) #Note: currently this requires manually changing col names in CSV
write.csv(submission, file = "C:/Users/Rich/OneDrive/Documents/Independent Projects/Kaggle/Walmart/kaggle_submission_boost.csv", row.names = FALSE)




