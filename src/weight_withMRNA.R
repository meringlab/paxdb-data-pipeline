# Merge all proteins (all=T) of all datasets of one species 
# and weight them (create integrated dataset).
# Get the correlation of the integrated dataset with mRNA.
#
# Author: Gabi
# Maintained by: Milan Simonovic <milan.simonovic@imls.uzh.ch>
#

###
### args: ###
args <- commandArgs(trailingOnly = T) # only after --args
#  1) dataset folder containing abundance files
# files must not have a header!!! 
path <- args[1]
#  2) output folder
output_folder <- args[2]
#  3) mRNA file
mrnaFile <- args[3]
#  4..n) dataset names
trailing = args[4:length(args)]
datasetNames = trailing[1:(length(trailing)/2)]
# then as many weights as there are dataset names, in the same order!
# NOTE parens are required around the whole expression! ((length(trailing)/2) + 1)
weights <- as.numeric(trailing[((length(trailing)/2) + 1):length(trailing)])
### args read ###


mRNA = read.delim(mrnaFile, header=F, col.names=c("protein","mRNA"))
## remove all rows with NA  (no value for the protein):
mRNA <- mRNA[!apply(is.na(mRNA), 1, any),]	
## get mRNA proteins without 0 values:
mRNA = mRNA[!(mRNA$mRNA == 0),]	                

## read file and label column names
## weight each datasets
## and merge all proteins of all files (all=T)

flag=1 #flag for merging (columns, which dataset..)
datasetFlag=data.frame() #flag for merging

for(names.i in datasetNames) {
    print(names.i, quote=F)
    filepathname = paste(path, names.i, sep="")	#sep=""  == no whitespace!
    print(filepathname, quote=F)
    ## some files have 3 columns, but we only need first 2, so, need to count
    num_cols = max(count.fields(filepathname, sep = "\t"))
    
    file = read.delim(filepathname, header=F, col.names=c("protein",names.i, rep("NULL", num_cols-2)))
    ## names.i might contain illegal characters for column names like -, so need to use col_names[2]
    col_names = colnames(file)[1:2]
    ## remove 3rd col:
    if (num_cols > 2) {
        file = file[,col_names]
    }
    
    ## weight the dataset
    file[,col_names[2]] = file[,col_names[2]]*weights[flag]
    
    ## merge all proteins of all files (all=T) 
    if (flag == 1 ) { 	        # only one dataset, can't merge only one; mark first dataset
        datasetFlag = file
    } else if (flag == 2) {	# merge first two datasets
        mergeFile = merge(datasetFlag, file, by="protein", all=T)
    } else {  			# merge the current dataset with the already merged datasets
        mergeFile = merge(mergeFile, file, by="protein", all=T) 
    }
    
    flag=flag+1
}


## create integrated dataset in new column
for ( i in 1:length(mergeFile$protein) ) { 
    mergeFile[i, (length(datasetNames)+2)] = sum(mergeFile[i,2:(length(datasetNames)+1)], na.rm=T) 
}	#ja waer a mit da flag gegangen, aber mei

## rename column name for new integrated dataset
names(mergeFile)[names(mergeFile)==paste("V",(length(datasetNames)+2), sep="")] <- "integratedDataset"

## normalize column with new integrated dataset (get ppm)
mergeFile$integratedDataset = mergeFile$integratedDataset / sum(mergeFile$integratedDataset, na.rm=T) * 1e+06

##write two files:
# 1. all columns (for control),
# 2. only proteinnames an abundance of integrated dataset (without header!)

weights_print=paste(weights, collapse='_',sep='_')
all_cols_file=paste(output_folder, 'mergedFile_weight_', weights_print,'_all.txt', sep='')
write.table(mergeFile, file=all_cols_file, quote=F, sep="\t", row.names=F)

write.table(mergeFile[,c(1,(length(datasetNames)+2))], file=paste(output_folder,"integrData_weighted_", weights_print,".txt", sep=""), quote=F, sep="\t", row.names=F, col.names=F)

#print(mergeFile[1:5,])
print("################# NEW FILE ########################", quote=F)
print("", quote=F)
print("weights of files: ", quote=F)
print(paste(as.numeric(commandArgs(trailingOnly = T)[6]), commandArgs(trailingOnly = T)[4]), quote=F)
print(paste(as.numeric(commandArgs(trailingOnly = T)[7]), commandArgs(trailingOnly = T)[5]), quote=F)
print("", quote=F)
print(paste("number proteins of integrated dataset: ", length(mergeFile$protein)), quote=F)
print("", quote=F)




#### Spearman correlation test: integrated dataset - mRNA

## merge mRNA with integrated data
print(paste("total number of mRNA: ", length(mRNA$protein)), quote=F)
print("", quote=F)

print("CORRELATION", quote=F)

mergeMRAN = merge(mRNA, mergeFile[,c(1,(length(datasetNames)+2))], by="protein")

## get the length of mRNA-merged dataset AND the correlation between dataset and mRNA
suppressWarnings( #only for no warning message
spearman <- cor.test(mergeMRAN$mRNA, mergeMRAN$integratedDataset,  m="spearman"))
spea_rho <- format(spearman$estimate, digits = 3)  

print(paste( names(mergeMRAN[2]), " - ", names(mergeMRAN[3])), quote=F)	 
print(paste("correlation:", spea_rho), quote=F)
print(c("shared mRNA proteins: ",length(mergeMRAN$protein)), quote=F)
print("", quote=F)


