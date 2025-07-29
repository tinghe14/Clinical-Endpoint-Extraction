import java.util.*;
import java.util.regex.*;
import java.util.stream.Collectors;

public final class compare1 {

    // private SizeFinder() {
    // }

    // Regular expressions
    static private final String VALUE_REGEX = "\\d+(?:\\.\\d+)?"; // \\d+ one or more digits, \\. match a decimal point, ? match zero or one of the preceding element
    static private final String UNIT_REGEX = "\\s*(mm|cm)"; // \\s* zero or more whilespace, (?:) is used for applying quantifiers or logical OR operations without the need to capture the match.
    static private final String DIM_REGEX = "\\s*[x\\*]\\s*"; // []match any one of the enclosed characters, x and \\* is a special character

    static private final String FRONT_REGEX = "(?:\\b|\\(|\\[|\\{)"; // non-caputuring group, a word boundary, (, [, or { can precede the size pattern
    static private final String BACK_REGEX = "(?:\\b|,|\\.|\\?|!|\\)|\\]|\\})";
    static private final String FULL_REGEX = FRONT_REGEX + VALUE_REGEX + "(?:" + "(?:" + UNIT_REGEX + "){0,1}" + DIM_REGEX + VALUE_REGEX + "){0,2}" + UNIT_REGEX + BACK_REGEX;

    static private final Pattern FULL_PATTERN = Pattern.compile(FULL_REGEX, Pattern.CASE_INSENSITIVE);

    static private final String[] SIZE_STOP_WORD_ARRAY = { "distance", "from", "superior", "inferior", "anterior", "posterior" };
    static private final int STOP_DISTANCE = 20; //15

    static public void addSentenceSizes(final String sentenceText) {
        final String lowercasedText = sentenceText.toLowerCase();
        final Collection<Integer> stopIndices = Arrays.stream(SIZE_STOP_WORD_ARRAY)
                .map(lowercasedText::indexOf)
                .filter(i -> i >= 0)
                .collect(Collectors.toList());
        final Matcher fullMatcher = FULL_PATTERN.matcher(lowercasedText);
        while (fullMatcher.find()) {
            boolean skip = false;
            for (int stopIndex : stopIndices) {
                if (Math.abs(fullMatcher.start() + (fullMatcher.end() - fullMatcher.start()) / 2 - stopIndex) < STOP_DISTANCE) {
                    skip = true;
                    break;
                }
            }
            if (!skip) {
                // filter by the preceding words
                String precedingText = lowercasedText.substring(0, fullMatcher.start());
                // range within 5 words
                String[] words = precedingText.split("\\s+");
                int wordsCount = words.length;
                StringBuilder context = new StringBuilder();
                for (int i = Math.max(0, wordsCount-5); i < wordsCount; i++){
                    context.append(words[i]).append(" ");
                }
                // TO-DO:
                // 1.check whether have "tumor" & "carcinoma" & "Thymoma" -> moma/noma?
                // 2.filter out, xxcm away from, xx from the nearest, eg: CARCINOMA, CLOSEST ANTERIOR MARGIN IS 7MM AWAY.
                // 3.negative eg: RESECTION MARGINS NEGATIVE FOR CARCINOMA (AT LEAST MORE THAN 2.0 CM).
                String contextStr = context.toString().trim();
                boolean containsTumor = contextStr.toLowerCase().contains("tumor");
                if (containsTumor){
                    System.out.println("Found size: " + sentenceText.substring(fullMatcher.start(), fullMatcher.end()));
                }
            }
        }
    }

    public static void main(String[] args) {
        System.out.println("hello, world");
        addSentenceSizes("After measuring, the tumor was found to be 5.3cm in diameter, with dimensions of 3 cm x 2 cm x 1.5 cm."); //3cm x 2cm x 1.5cm
        addSentenceSizes("INVASIVE DUCTAL CARCINOMA, 2.1 CM LEFT BREAST_URI");
        addSentenceSizes("DUCTAL CARCINOMA IN SITU, 900mm. RIGHT BREAST_URI 12:00.");
        System.out.println("test case");
        addSentenceSizes("Total Tumor size 1.4 cm x 1.9 cm");
        addSentenceSizes("Total Tumor size 1.4x1.9 cm");
        addSentenceSizes("INVASIVE DUCTAL CARCINOMA, 2.8 * 1.4 * 1.9 mm");
        addSentenceSizes("Spec. Taken. INTERPRETATION AND DIAGNOSIS: 1. LYMPH NODE, L8 (EXCISION) : ONE (1) LYMPH NODE AND ASSOCIATED. FIBROADIPOSE TISSUE, NEGATIVE FOR TUMOR. 2. LUNG (RESECTION) : SPECIMEN TYPE: Lobectomy, left lower lobe. TUMOR SITE: Left Lower lobe. HISTOLOGIC TYPE: Adenocarcinoma (70% Acinar, 30% solid). TUMOR SIZE: 2.3 cm. HISTOLOGIC GRADE: G3: Poorly Differentiated. LYMPH NODES: Metastatic carcinoma in 1 of 11 lymph nodes. EXTENT OF INVASION (7th Edition, AJCC) : PRIMARY TUMOR. pT1b: Tumor >2 cm but 3 cm of less. REGIONAL LYMPH NODES: pN1: Metastasis in ipsilateral peribronchial, hilar,. or intrapulmonary nodes, including those. involved by direct extension. DISTANT METASTASIS: pMx: Cannot be assessed. MARGINS. Margins uninvolved by invasive carcinoma. VENOUS/ARTERIAL (LARGE VESSEL) INVASION: Absent. LYMPHATIC (SMALL VESSEL) INVASION: Indeterminate. 3. LYMPH NODE, STATION 6 (EXCISION) : TWO (2) LYMPH NODES AND. ASSOCIATED FIBROADIPOSE TISSUE, NEGATIVE FOR TUMOR. 4. LYMPH NODE, STATION 7 (EXCISION) : ONE (1) LYMPH NODE AND. ASSOCIATED FIBROADIPOSE TISSUE, NEGATIVE FOR TUMOR. 5. LYMPH NODE, L10 (EXCISION) : ONE (1) LYMPH NODE AND ASSOCIATED. FIBROADIPOSE TISSUE, NEGATIVE FOR TUMOR. Note: A movat stain was reviewed. This case was shown at the. KRAS, EGFR and ALK molecular analysis. have been ordered and will be reported in an addendum. ADDENDUM: RESULTS OF ALK FISH ANALYSIS : NEGATIVE. THIS RESULT SHOWED NO EVIDENCE OF REARRANGEMENT OF THE ALK GENE. A COPY OF THE COMPLETE REPORT IS AVAILABLE IN. AND IS ON FILE IN. ADDENDUM: F. F. SOURCE: TEST: EGFR MUTATION ANALYSIS. EGFR MUTATION ANALYS. Specimen Number : Referring #: ICD9 Code: Tissue. Probe. %pat. 2SD. Slides. EGFR. POSITIVE. Consultant Date: Consultant's Findings: A .22352249del .E746 A750del) mutation was. detected in Exon 19 of the EGFR gene. This mutation is. reported to correlate with RESPONSIVENESS to EGFR. tyrosine kinase inhibitor therapies in patients with non-small- -. cell lung cancer. Mutations in the tyrosine kinase domain of the epidermal. growth factor receptor (EGFR) gene are reported to be. associated with differential responsiveness/resistance to. targeted therapeutics for non-small-cell lung cancer. (NSCLC) . Most data published pertain to Gefitinib. Similar. data have been seen in studies using Erlotinib. This test is validated for non-small cell lung carcinoma. The clinical significance and utility of this test in other. tumor types is unknown. Method: This assay analyzes exons 18-21 of the EGFR. tyrosine kinase domain. Based on current literature, the vast. majority of mutations are expected to occur in these exons. Tissue sections are reviewed by a pathologist and relevant. tumor is selected for analysis. DNA is extracted from the. tissue and subject to PCR amplification using primers to. exons 18-21 of the EGFR gene. The amplification products. are analyzed by bi-directional direct DNA. sequencing using capillary gel electrophoresis and. fluorescence detection. The analytical sensitivity of the. assay is 20% mutant alleles, or 40% tumor cells with a. heterozygous mutation; mutations present in a low. percentage of cells may not be detected. References: Pao W and Miller VA. J Clin Oncol. 2005; 23:2556-2568. Lynch TJ , et al. N Eng J Med. 2004; 350:2129-2139. Paez JG, et al. Science. 2004; 304:1497-1500. Sharma SV, et al. Nat Rev Cancer. 2007; 7:169-180. This test was developed and its performance characteristics. determined by. It has. not been cleared or approved by the U.S. Food and Drug. Administration. The FDA has determined that such. clearance or approval is not necessary. This test is used for. clinical purposes. It should not be regarded as. investigational or for research. COMMENT: Interpretation and recommendation provided by: Assistant Professor, Department of Pathology. Test performed by. Clinical History: HISTORY OF PET POSITIVE LEFT LOWER LOBE LESION. GROSS DESCRIPTION. PART #1: L 8 LYMPH NODE. Resident Pathologist: : The specimen for Part 1 is received in formalin, labeled with the. patient's name,. land designated 'L-8 Lymph Node. ' The. specimen consists of one (1) piece of red-tan-gray soft tissue. measuring 1 x 0.8 x 0.5 cm. The specimen is submitted in its entirety. SUMMARY OF SECTIONS: 1 - A. - 1. (ENTIRETY OF SPECIMEN). 1 - TOTAL - 1. PART #2: LEFT LOWER LOBE. Resident Pathologist: The specimen for Part 2 is received in formalin, labeled with the. patient's name,. and designated 'Left Lower Lobe. f The. specimen consists of a 15.0 x 15.0 x 2.5 cm grossly recognizable lung. lobe weighing 167.5 gm. The pleural surface is red-purple, wrinkled. and glistening. A surgical incision is present over a grossly. apparent mass which measures 2.3 x 2.0 x 1.5 cm. The pleural surface. overlying this mass appears puckered. The pleural surface overlying. the tumor mass is inked black. This tumor is located in the superior. aspect of the lobe, approximately 1.8 cm from the bronchial margin. Three (3) staple lines are present on the lung measuring 6 cm, 4 cm. and 2 cm. The first two (2) staple lines are removed to reveal. underlying grossly unremarkable lung parenchyma which is inked. orange. The third staple line contains vessels which are sectioned. and submitted. A shave section of the bronchial margin is also taken. No grossly identifiable hilar lymph nodes are present. The tumor. nodule is thoroughly serially sectioned to reveal that it abuts the. pleura and is 0.4 cm from the surgical resection margin. The tumor. mass appears to surround large vessels in the lung parenchyma. Representative sections of tumor relative to pleura, vessels, and. surgical resection margin are submitted. Serially sectioning through. the remaining lung tissue identified two (2) subpleural nodules which. were suspicious for tumor involvement. Representative sections are. submitted. No other masses or lesions are identified within the lung. The uninvolved lung parenchyma appears tan-red and grossly. unremarkable. Representative sections of the uninvolved lung are. submitted. SUMMARY OF SECTIONS: 1 - A. - 1. (BRONCHIAL MARGIN). 1 - B. - 1. (VASCULAR MARGINS). 2 - C&D. - 1 EA. (TUMOR IN RELATION TO PLEURA AND VESSELS). 2 - E&F. - 1. EA (TUMOR IN RELATION TO SURGICAL RESECTION MARGIN). 2 - G&H. 1 EA. (SUBPLEURAL NODULES). 2 - I&J. 1 EA (REPRESENTATIVE SECTIONS OF UNINVOLVED LUNG). 12 - TOTAL - 12. PART #3: STATION 6 LYMPH NODE. Resident Pathologist: The specimen for Part 3 is received in formalin, labeled with the. patient's name,. and designated 'Station 6 Lymph Node. 1. The specimen consists of multiple pieces of red-tan-yellow soft. tissue measuring 1.8 x 1. 1 x 0.3 cm in aggregate. The specimen is. submitted in its entirety. SUMMARY OF SECTIONS: 1 - A. - M. (ENTIRETY OF SPECIMEN). 1 - TOTAL - MULTIPLE. PART #4: STATION 7 LYMPH NODE. Resident Pathologist: The specimen for Part 4 is received in formalin, labeled with the. patient' name,. and designated 'Station 7 Lymph Node. The specimen consists of one (1) piece of red-tan-brown soft tissue. measuring 1.4 x 0.7 x 0.3 cm. The specimen is submitted in its. entirety. SUMMARY OF SECTIONS: 1 - A. - 1. (ENTIRETY OF SPECIMEN). 1 - TOTAL - 1. PART #5: L 10 LYMPH NODE. Resident Pathologist: The specimen for Part 5 is received in formalin, labeled with the. patient's name,. and designated 'L-10 Lymph Node. 1 The. specimen consists of one (1) piece of red-tan-brown soft tissue. measuring 1.4 x 1.2 x 0.4 cm. One hundred percent (100%) of the specimen is submitted. SUMMARY OF SECTIONS: 1 - A. - 1. (ENTIRETY OF SPECIMEN). 1 - TOTAL - 1. Other Surgical Pathology Specimens known to the computer: printed.");
    }
}
