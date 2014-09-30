# Merge all proteins (all=T) of 2 datasets and weight them (create integrated dataset).
# Get the correlation of the integrated dataset with mRNA.
#
# Author: Gabi
# Maintained by: Milan Simonovic <milan.simonovic@imls.uzh.ch>
#

###
### args: ###
args <- commandArgs(trailingOnly = T) # only after --args
#  1) mRNA file
mrnaFile <- args[1]

#  2) output 
output_folder <- args[2]

#  3) 1st dataset (must not have a header)
d1 <- args[3]
d2 <- args[4]

# 4) weights for d1, d2 (in that order!)
weights <- c(as.numeric(args[5]), as.numeric(args[6]))
### args read ###

datasetNames = c(basename(d1), basename(d2))

mRNA = read.delim(mrnaFile, header=F, col.names=c("protein","mRNA"))
## remove all rows with NA  (no value for the protein):
mRNA <- mRNA[!apply(is.na(mRNA), 1, any),]	
## get mRNA proteins without 0 values:
mRNA = mRNA[!(mRNA$mRNA == 0),]	                

## read file and label column names
## weight each datasets
## and merge all proteins of all files (all=T)

weightDataset <- function(dataset, weight=1.0){
    ## some files have 3 columns, but we only need first 2, so, need to count
    num_cols = max(count.fields(dataset, sep = "\t"))
    
    file = read.delim(dataset, header=F, col.names=c("protein",basename(dataset), rep("NULL", num_cols-2)))
    ## names.i might contain illegal characters for column names like -, so need to use col_names[2]
    col_names = colnames(file)[1:2]
    ## remove 3rd col:
    if (num_cols > 2) {
        file = file[,col_names]
    }
    file[,col_names[2]] = file[,col_names[2]]*weight
    return (file)
}
f1=weightDataset(d1, weights[1])
f2=weightDataset(d2, weights[2])
mergeFile = merge(f1, f2, by="protein", all=T)

## create integrated dataset in new column
for ( i in 1:length(mergeFile$protein) ) { 
    mergeFile[i, (length(datasetNames)+2)] = sum(mergeFile[i,2:(length(datasetNames)+1)], na.rm=T) 
}	#ja waer a mit da flag gegangen, aber mei

## rename column name for new integrated dataset
names(mergeFile)[names(mergeFile)==paste("V",(length(datasetNames)+2), sep="")] <- "integratedDataset"

## normalize column with new integrated dataset (get ppm)
mergeFile$integratedDataset = mergeFile$integratedDataset / sum(mergeFile$integratedDataset, na.rm=T) * 1e+06

# write only proteinnames and abundance (without a header!)
weights_print=paste(weights, collapse='_',sep='_')
output_file = paste(output_folder,"integrData_weighted_", weights_print,".txt", sep="")

write.table(mergeFile[,c(1,(length(datasetNames)+2))], file=output_file, quote=F, sep="\t", row.names=F, col.names=F)

#### Spearman correlation test: integrated dataset - mRNA
#
## merge mRNA with integrated data
#print(paste("total number of mRNA: ", length(mRNA$protein)), quote=F)
mergeMRAN = merge(mRNA, mergeFile[,c(1,(length(datasetNames)+2))], by="protein")

## get the length of mRNA-merged dataset AND the correlation between dataset and mRNA
suppressWarnings( #only for no warning message
spearman <- cor.test(mergeMRAN$mRNA, mergeMRAN$integratedDataset,  m="spearman"))
spea_rho <- format(spearman$estimate, digits = 3)  

#print(c("shared mRNA proteins: ",length(mergeMRAN$protein)), quote=F)
#print(spea_rho, quote=F)

cat(output_file, '\n') 
cat(spea_rho) #just print the number




