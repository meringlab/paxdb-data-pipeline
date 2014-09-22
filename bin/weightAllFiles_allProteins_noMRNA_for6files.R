#to execute this script in R console write  
#        source('~/testBASH/2weightAllFiles_allProteins_for3files.R') 


#MERGE ALL PROTEINS (all=T) OF ALL DATASETS OF ONE SPECIES AND WEIGHT IT  -> CREATE INTEGRATED DATASET
#GET THE CORRELATION OF THE INTEGRATED DATASET WITH mRNA



# REPLACE path for the abundance files
path <- commandArgs(trailingOnly = T)[1]


# REPLACE path for output files
pathOutput <- commandArgs(trailingOnly = T)[2]

# REPLACE datasetnames() -> use original abundancefile names without .txt ending
# --> files should not have a header!!!
datasetNames <- c(commandArgs(trailingOnly = T)[3], commandArgs(trailingOnly = T)[4], commandArgs(trailingOnly = T)[5], commandArgs(trailingOnly = T)[6], commandArgs(trailingOnly = T)[7], commandArgs(trailingOnly = T)[8])


# REPLACE weights, use same order as datasetNames() #e.g. 100% == 1; 50% == 0.5; 1% == 0.01
weights <- c(as.numeric(commandArgs(trailingOnly = T)[9]), as.numeric(commandArgs(trailingOnly = T)[10]), as.numeric(commandArgs(trailingOnly = T)[11]), as.numeric(commandArgs(trailingOnly = T)[12]), as.numeric(commandArgs(trailingOnly = T)[13]), as.numeric(commandArgs(trailingOnly = T)[14]))




# # # # # # #-----------of here nothing must be modified---------------------



## read file and label column names
## weight each datasets
## and merge all proteins of all files (all=T)

flag=1 #flag for merging (columns, which dataset..)
datasetFlag=data.frame() #flag for merging

for(names.i in datasetNames) {
	#print(names.i, quote=F)
	filepathname = paste(path, names.i, ".txt", sep="")	#sep=""  == no whitespace!
	#print(filepathname, quote=F)

	file = read.delim(filepathname, header=F, col.names=c("protein",names.i))
	
## weight the dataset
	file[,names.i] = file[,names.i]*weights[flag]
	
## merge all proteins of all files (all=T) 
	if (flag == 1 ) { datasetFlag = file } 												#only one dataset, can't merge only one; mark first dataset
	else if (flag == 2) { mergeFile = merge(datasetFlag, file, by="protein", all=T)	} 	#merge first two datasets
	else { mergeFile = merge(mergeFile, file, by="protein", all=T) } 					#merge the current dataset with the already merged datasets   # dont need this for two files..... well

	flag=flag+1
}


## create integrated dataset in new column
for ( i in 1:length(mergeFile$protein) ) { mergeFile[i,(length(datasetNames)+2)]= sum(mergeFile[i,2:(length(datasetNames)+1)] ,na.rm=T) }	


## rename column name for new integrated dataset
names(mergeFile)[names(mergeFile)==paste("V",(length(datasetNames)+2), sep="")] <- "integratedDataset"


## normalize column with new integrated dataset (get ppm)
mergeFile$integratedDataset = mergeFile$integratedDataset / sum(mergeFile$integratedDataset, na.rm=T) * 1e+06


##write two files:
# 1. all columns (for control),
# 2. only proteinnames an abundance of integrated dataset (without header!)
write.table(mergeFile, file=paste(pathOutput, "mergedFile_weight_", as.numeric(commandArgs(trailingOnly = T)[9]), "_", as.numeric(commandArgs(trailingOnly = T)[10]), "_", as.numeric(commandArgs(trailingOnly = T)[11]), "_", as.numeric(commandArgs(trailingOnly = T)[12]), "_", as.numeric(commandArgs(trailingOnly = T)[13]), "_", as.numeric(commandArgs(trailingOnly = T)[14]),"_all.txt", sep=""), quote=F, sep="\t", row.names=F)
write.table(mergeFile[,c(1,(length(datasetNames)+2))], file=paste(pathOutput,"integrData_weighted_", as.numeric(commandArgs(trailingOnly = T)[9]), "_", as.numeric(commandArgs(trailingOnly = T)[10]), "_", as.numeric(commandArgs(trailingOnly = T)[11]), "_", as.numeric(commandArgs(trailingOnly = T)[12]), "_", as.numeric(commandArgs(trailingOnly = T)[13]), "_", as.numeric(commandArgs(trailingOnly = T)[14]),".txt", sep=""), quote=F, sep="\t", row.names=F, col.names=F)








