import java.util.*;
import java.util.regex.*;
import java.util.stream.Collectors;

public final class compare2 {

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
                System.out.println("Found size: " + sentenceText.substring(fullMatcher.start(), fullMatcher.end()));
            }
        }
    }

    public static void main(String[] args) {
        System.out.println("test case");
        addSentenceSizes("After measuring, the tumor was found to be 5.3cm in diameter, with dimensions of 3 cm x 2 cm x 1.5 cm.");
        addSentenceSizes("INVASIVE DUCTAL CARCINOMA, 2.1 CM LEFT BREAST_URI");
        addSentenceSizes("DUCTAL CARCINOMA IN SITU, 900mm. RIGHT BREAST_URI 12:00.");
        addSentenceSizes("Total Tumor size 1.4 cm x 1.9 cm");
        addSentenceSizes("Total Tumor size 1.4x1.9 cm");
        addSentenceSizes("INVASIVE DUCTAL CARCINOMA, 2.8 * 1.4 * 1.9 mm");
    }
}

