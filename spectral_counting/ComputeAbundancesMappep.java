/**
 * @author manuelw
 * compute protein abundances based on a fasta file and a list of peptides
 */

import java.io.FileNotFoundException;
import java.io.FileReader;
import java.io.BufferedReader;
import java.io.IOException;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.ArrayList;
import java.util.Map;

public class ComputeAbundancesMappep {

	/**
	 * @param args
	 */
	private static Map<String, Map<String, Double>> protein2peptideCount = new HashMap<String, Map<String, Double>>();
	private static Map<String, HashSet<String>> peptideLookup = new HashMap<String, HashSet<String>>();
	private static Map<String, String> sequences = new HashMap<String, String>();
	private static Map<String, Integer> peptideCount = new HashMap<String, Integer>();
	private static Map<Integer, Integer> allPepLengths = new HashMap<Integer, Integer>();
	private static Map<Integer, Integer> observedPepLengths = new HashMap<Integer, Integer>();
	private static Map<Integer, Double> PepLengthFactor = new HashMap<Integer, Double>();
	private static Map<String, Double> proteinAbundance = new HashMap<String, Double>();
	private static String species = "";
	private static String pepFile;
	private static String fastaFile;
	private static boolean normalize = true;
	private static int prefixSize = 6;

	public static void main(String[] args) throws IOException {
		
		if (args.length < 2) {
			printHelp();
			return;
		}
		
		// treat command line options
		ArrayList<String> a = new ArrayList<String>(Arrays.asList(args));
		for (int i = 0; i < a.size(); i++) {
			String s = a.get(i);
			if (s.equalsIgnoreCase("-h") || s.equalsIgnoreCase("--help")) {
				printHelp();
				return;
			}
			if (s.equalsIgnoreCase("-s") || s.equalsIgnoreCase("--string")) {
				a.remove(i);
				species = a.remove(i--);
			}
			if (s.equalsIgnoreCase("-p") || s.equalsIgnoreCase("--prefix")) {
				a.remove(i);
				prefixSize = Integer.parseInt(a.remove(i--));
			}
			if (s.equalsIgnoreCase("-n") || s.equalsIgnoreCase("--nonorm")) {
				a.remove(i--);
				normalize = false;
			}
		}
		
		pepFile = a.get(0);
		fastaFile = a.get(1);
		
		readPeptides(pepFile);
		readFasta(fastaFile);
		mapPeptides();
		digestFasta();
		calcPepLengthFactor();

		// calculate all protein abundances
		double total = 0;
		for (String p : protein2peptideCount.keySet()) {
			double coverage = weightedProteinCoverage(p);
			if (coverage != -1.0) {	// failed for whatever reason
				proteinAbundance.put(p, coverage);
				total += coverage;
			}
		}

		// print normalized values
		//for (String p : proteinAbundance.keySet()) {
		//	if (normalize)
			    //		System.out.println(p + "\t" + proteinAbundance.get(p) * 1e6 / total);
		//	else
		//		System.out.println(p + "\t" + proteinAbundance.get(p));
		// }
	}

	private static void printHelp() {
		System.err.println("\nComputeAbundances [options] <peptide list> <fasta file>");
		System.err.println("(it needs quite a lot of memory, you might want to run it with -Xms512m -Xmx512m -Xss256k)");
		System.err.println("\nOptions are:");
		System.err.println("-h | --help\t\t\tto see this message");
		System.err.println("-s | --string <species id>\tfasta file is in STRING format (species_id.protein_id), use this species id");
		System.err.println("-n | --nonorm\t\t\tdo NOT normalize abundance values to ppm");
		System.err.println("-p | --prefix <size>\t\t\tset prefix size for lookup table - must be >= shortest peptide (default: 6)");
		System.err.println("Note: the peptide list should be in the format <peptide sequence>\\t<count>\n");
	}
	
	private static double weightedProteinCoverage(String protein) {
		if (!protein2peptideCount.containsKey(protein))
			return -1.0;
		double peptide_count = 0.0;
		double peptide_coverage = 0.0;
		for (String pep : protein2peptideCount.get(protein).keySet()) {
			peptide_count += protein2peptideCount.get(protein).get(pep) * pep.length();
//			System.err.println("* " + pep + "\t" + peptideCount.get(protein).get(pep));
		}
		if (peptide_count == 0.0 || !sequences.containsKey(protein))
			return -1.0;
		double adjusted_length = 0.0;
		for (String pep : sequences.get(protein).split("R|K")) {
			int len = pep.length() + 1;
			if (len >= 7 && len <= 40 && PepLengthFactor.containsKey(len))	// counting only peptides that are detectable by mass spectrometry
				adjusted_length += len * PepLengthFactor.get(len);
		}
		if (adjusted_length == 0.0)
			return -1.0;
//		System.err.println("adjusted length: " + adjusted_length);
//		System.err.println("peptide count: " + peptide_count);
		peptide_coverage = peptide_count / adjusted_length;
		return peptide_coverage;
	}
	
	private static void digestFasta() {
		if (sequences.isEmpty()) {
			System.err.println("** error: no sequences read from fasta file");
			System.exit(0);
		}
		for (final String p : sequences.values() ) {
			// System.out.println("* " + p + "\\npeps:");
			for (String pep : p.split("R|K")) {
				// System.out.println("- " + pep);
				int len = pep.length() + 1;	// pep.length() + 1 because pep does not contain final R/K
				if (allPepLengths.containsKey(len))
					allPepLengths.put(len, 1 + allPepLengths.get(len));
				else
					allPepLengths.put(len, 1);
			}
		}
	}

	private static void calcPepLengthFactor() {
		for (int len : observedPepLengths.keySet()) {
			PepLengthFactor.put(len, (double) observedPepLengths.get(len) / allPepLengths.get(len));
		}
	}
	
	private static void readFasta(final String filename) throws FileNotFoundException, IOException {

		System.err.println("reading fasta file...");
		
		BufferedReader reader = new BufferedReader(new FileReader(filename));
	    String line;
    	String id = "";
	    String seq = "";
	    while ((line = reader.readLine()) != null) {
	    	if (line.trim().isEmpty() || line.matches("^\\s*#.*"))	// empty line or comment (technically not legal in fasta file)
	    		continue;
	    	if (line.trim().startsWith(">")) {	// new entry
	    		if ( !id.isEmpty() && !seq.isEmpty() ) {	// store previous entry in HashMap
		    		if (species.isEmpty()) // regular fasta file
		    			sequences.put(id, seq);
		    		else {										// we're reading a STRING format fasta file (species_id.protein_id)
		    			if (id.startsWith(species + ".")) {	// right species - store this entry
		    				id = id.substring(species.length() + 1);	// remove species id
			    			sequences.put(id, seq);
		    			}
		    		}
	    		}
	    		id = line.split("\\s", 2)[0].trim().substring(1);
	    		seq = "";
	    	}
	    	else {
	    		seq += line.trim();
	    	}
	    }
		if ( !id.isEmpty() && !seq.isEmpty() ) {	// store last entry in HashMap
    		if (species.isEmpty()) // regular fasta file
    			sequences.put(id, seq);
    		else {										// we're reading a STRING format fasta file (species_id.protein_id)
    			if (id.startsWith(species + ".")) {	// right species - store this entry
    				id = id.substring(species.length() + 1);	// remove species id
	    			sequences.put(id, seq);
    			}
    		}
		}
		System.err.println("* no of sequences read from " + filename + ": " + sequences.size());
	}
	
	private static void readPeptides(final String filename) throws FileNotFoundException, IOException {
		BufferedReader reader = new BufferedReader(new FileReader(filename));
	    String line;
	    int line_count = 0;
	    while ((line = reader.readLine()) != null) {
	    	if (line.trim().isEmpty() || line.matches("^\\s*#.*"))	// empty line or comment
	    		continue;
	    	String [] fields = line.split("\t");

	    	String pepseq = fields[0].trim();
	    	if (pepseq.isEmpty()) {
	    		System.err.println("error parsing " + filename + ": empty peptide sequence in: " + line.trim());
	    		continue;
	    	}
	    	
	    	int number = 0;
	    	try {
	    		number = Integer.parseInt(fields[1]);
	    	} catch (ArrayIndexOutOfBoundsException e) {
	    		System.err.println("error parsing " + filename + ": second column entry missing in: " + line.trim());
	    		continue;
	    	} catch (NumberFormatException e) {
	    		System.err.println("error parsing " + filename + ": second column not an integer: " + line.trim());
	    		continue;
	    	}
	    		
	        // put into lookup table:
	    	String lookup = "";
	    	try {
	    		lookup = pepseq.substring(0, prefixSize);
	    	} catch (StringIndexOutOfBoundsException e) {
	    		System.err.println("error: lookup prefix longer than shortest peptide - set to smaller value with -p/--prefix (default: 6)");
	    		System.exit(1);
	    	}
	        if (!peptideLookup.containsKey(lookup))
	        	peptideLookup.put(lookup, new HashSet<String>());
	        peptideLookup.get(lookup).add(pepseq);
	        
	        peptideCount.put(pepseq, number);
	        line_count++;
	    }
		System.err.println("* no of peptides read from " + filename + ": " + line_count);
	}

	
	private static void mapPeptides() {

		final Map<String, HashSet<String>> peptide2protein = new HashMap<String, HashSet<String>>();

		System.err.println("remapping peptides...");
		int total = sequences.size();
		int count = 0;
		int step = 10;
		for (final String id : sequences.keySet()) {
			String seq = sequences.get(id);
			for (int i = 0; i < seq.length() - prefixSize; i++) {
				String sub = seq.substring(i, i + prefixSize);
				if (peptideLookup.containsKey(sub)) {	// are there any matching prefixes?
					// if yes, check whether any peptide matches the protein:
					HashSet<String> peps = peptideLookup.get(sub);
					for (final String peptide : peps.toArray(new String[peps.size()])) {
						if (seq.regionMatches(i, peptide, 0, peptide.length())) {
							if (!peptide2protein.containsKey(peptide))
								peptide2protein.put(peptide, new HashSet<String>());
							peptide2protein.get(peptide).add(id);
							System.out.println(id + "\t " + peptide + "\t"+peptideCount.get(peptide));
						}
					}
				}
			}
			if (count * 100 / total > step) {
				System.err.println(step + "% done");
				step += 10;
			}
			count++;
		}	
		System.err.println("100% done");
		
		for (final String pep : peptide2protein.keySet()) {
			for (final String protein : peptide2protein.get(pep)) {
				if (!protein2peptideCount.containsKey(protein))
					protein2peptideCount.put(protein, new HashMap<String, Double>());
				protein2peptideCount.get(protein).put(pep, (double) peptideCount.get(pep) / peptide2protein.get(pep).size());
			}
	        // for length distribution of peptides:
	        if (observedPepLengths.containsKey(pep.length()))
	        	observedPepLengths.put(pep.length(), peptideCount.get(pep) + observedPepLengths.get(pep.length()) );
	        else
	        	observedPepLengths.put(pep.length(), peptideCount.get(pep));
		}
	}
}