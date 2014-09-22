

#MERGE EACH FILE WITH MRNA AND CALCULATE CORRELATION
	   					


# REPLACE path for the abundance files
path <- commandArgs(trailingOnly = T)[1]


# REPLACE mRNA file
mRNA = read.delim(commandArgs(trailingOnly = T)[2], header=F, col.names=c("protein","mRNA"))
mRNA <- mRNA[!apply(is.na(mRNA), 1, any),]	#remove all rows with NA  (no value for the protein)
mRNA = mRNA[!(mRNA$mRNA == 0),]	#get mRNA proteins without 0 values


# REPLACE datasetnames() -> use original abundancefile names without .txt ending
# --> files should not have a header!!!
datasetNames <- c(commandArgs(trailingOnly = T)[3], commandArgs(trailingOnly = T)[4], commandArgs(trailingOnly = T)[5], commandArgs(trailingOnly = T)[6])#'Spombe_Alex_2012_09_spectral_count')



# # # # # # #-----------off here nothing must be modified---------------------

print("", quote=F)
print(paste("number proteins of mRNA:", length(mRNA$protein)), quote=F)
print("", quote=F)
print("CORRELATIONS", quote=F)
print("", quote=F)


## read file and label column names
## and create merged file of each dataset with mRNA 
## and get ppm
## get mRNA correlation

selectColumn=1 #select column for outputfile
for(names.i in datasetNames) {
	selectColumn=selectColumn+1
	#print(names.i, quote=F)
	filepathname = paste(path, names.i, ".txt", sep="")	#sep=""  == no whitespace!
	#print(filepathname, quote=F)

	file = read.delim(filepathname, header=F, col.names=c("protein",names.i))
	
## create merged file
	mergedFile = merge(file, mRNA, by="protein")

## get ppm
	mergedFile[,names.i] = mergedFile[,names.i] / sum(mergedFile[,names.i], na.rm=T) * 1e+06
	mergedFile$mRNA = mergedFile$mRNA / sum(mergedFile$mRNA, na.rm=T) * 1e+06
	
## get the length of each mRNA-merged dataset AND the correlations between each dataset and mRNA
	suppressWarnings( #only for no warning message
	spearman <- cor.test(mergedFile$mRNA, mergedFile[,names.i],  m="spearman"))
	spea_rho <- format(spearman$estimate, digits = 3)  

	print(paste( names.i, " - mRNA"), quote=F)
	print(paste("correlation:", spea_rho), quote=F)
	print(c("used proteins: ",length(mergedFile$protein)), quote=F)
	print("", quote=F)
}











