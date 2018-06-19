from Bio import SeqIO
def slicefastafilebyspecid(speid):
   handle = open("./../protein.sequences.v9.0.fa", "rU")
   for record in SeqIO.parse(handle, "fasta") :
      recordspeid = ((record.id).split('.'))[0]
      if recordspeid == speid:
         
         handle.closed()
