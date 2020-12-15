#
# This script is used to generate Python tests.
#
# The output generated by each test can be seen at:
#
# https://github.com/ialbert/bio/tree/master/test/data
#

# Stop on errors.
set -uex

# Delete the ncov data if exists.
bio ncov --delete

# Fetch the accession, rename the data and change the sequence id.
bio NC_045512 --fetch --rename ncov --seqid ncov

# Shows the internal JSON format of the data.
bio ncov --json > ncov.json

# Convert to GenBank.
bio ncov --genbank > ncov.gb

# Convert to FASTA.
bio ncov --fasta > ncov.fa

# Convert to GFF.
bio ncov --gff > ncov.gff

# Match with regular expression.
bio ncov --gff --match phosphoesterase  > match.gff

# Convert features associated with a gene to GFF.
bio ncov --gff --gene S > gene.gff

# Convert to GFF features that overlap with start to end.
bio ncov --gff  --start 10000 --end 20000 > overlap.gff

# Numbers may have commas.
bio ncov --gff  --start 10,000 --end 20,000 > overlap.gff

# Numbers may be expressed with prefixes.
bio ncov --gff  --start 10kb --end 20kb > overlap.gff

# Convert to GFF by type.
bio ncov --gff  --type CDS > cds.gff

# Convert to GFF by multiple types.
bio ncov --gff  --type gene,CDS,mRNA > manytypes.gff

# Slice a FASTA to a region and change the sequence id.
bio ncov --fasta --seqid foo --start 10 --end 20 > start.fa

# Convert to FASTA features with a certain type.
bio ncov --fasta --type CDS -end 10 > cds.fa

# Convert to FASTA a sub region of type filtered data.
bio ncov --fasta --type gene --end 10 > start-gene.fa

# Translate the DNA for features that have the type CDS.
bio ncov --fasta --translate --type CDS --end 10 > translates.fa

# Extract already translated proteins from the data.
# The translation attribute must be filled in GenBank.
bio ncov --fasta --protein --start -10 > protein-end.fa

# Coding sequences for a gene.
bio ncov --fasta --type CDS --gene S --end 10 > cds-gene.fa

# Shorcut1, all CDS that is labeled with gene=S
bio ncov:S --fasta --end 10 >  cds-gene.fa

# Another shortcut, this time we access coding sequences by the id.
bio ncov --id YP_009724390.1 --fasta --end 10 >  cds-gene.fa

# Extract the already traslated protein from the data.
bio ncov:S --fasta --protein --seqid foo > cds-prot.fa

# Interactive mode. Data obtained from the command line paramter
bio ATGGGC -i --fasta > inter.fa

# Translate in interactive mode.
bio ATGGGC -i --translate --seqid foo >  inter-trans.fa

# Translate on the reverse complement.
bio ATGGGC -i --revcomp --translate --seqid foo > inter-revcomp1.fa

# You can separately reverse and complement
bio ATGGGC -i --reverse --complement --translate --seqid foo >  inter-revcomp2.fa

# Get the RaTG13 data.
bio MN996532 --fetch --rename ratg13 --seqid ratg13

# Align the first 200 bp across both genomes.
bio ncov ratg13 --end 180 --align > align-dna.txt

# Align the DNA for the coding sequences of the S protein.
bio ncov:S ratg13:S --end 180 --align > align-gene.txt

# Align the translated DNA for the coding sequences of the S protein.
bio ncov:S ratg13:S --end 180 --translate --align > align-translation.txt

# Generate one letter peptide trace above the DNA
bio ratg13:S ncov:S  --end 180 --align -1 > align-gene-pept1.txt

# Generate three letter peptide trace above the DNA
bio ratg13:S ncov:S  --end 180 --align -3 > align-gene-pept3.txt

# Align the already translated proteins.
bio ncov:S ratg13:S --protein --end 60 --align > align-protein.txt

# Local alignment in interactive mode.
bio THISLINE ISALIGNED  -i --align --local > align-local.txt

# Global alignment in interactive mode.
bio THISLINE ISALIGNED -i --align --global > align-global.txt

# Semiglobal alignment in interactive mode.
bio THISLINE ISALIGNED -i --align --semiglobal > align-semiglobal.txt

# Check taxonomy defaults
bio 9606 --taxon > taxon_9606.txt

# Generate lineage.
bio 9606 --lineage --taxon > taxon_9606_lineage.txt

# The lineage may be flattened to a single line.
bio 9606 --lineage --flat --taxon > taxon_9606_flat_lineage.txt

# Taxonomy information from data.
bio ncov ratg13 --taxon > taxon_data.txt

# Remove the old ebola if exists.
bio ebola --delete

# Fetch and rename the ebola data.
bio KM233118 --fetch --rename ebola

# Get the links to the data.
bio ebola --sra > sra-test.txt

