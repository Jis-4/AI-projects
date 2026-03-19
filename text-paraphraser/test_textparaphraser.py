import unittest
from textparaphraser import paraphrase

class TestParaphraser(unittest.TestCase):

    def test_paraphrase_changes_sentence(self):
        """
        Test that paraphrasing a sentence results in a different sentence.
        Note: This test might occasionally fail if, by chance, no words are replaced
        or words are replaced by identical-looking synonyms.
        """
        original_sentence = "The quick brown fox jumps over the lazy dog because it was very energetic."
        paraphrased_sentence = paraphrase(original_sentence)
        self.assertNotEqual(original_sentence, paraphrased_sentence, "Paraphrased sentence should ideally be different from the original.")
        self.assertIsInstance(paraphrased_sentence, str)

    def test_paraphrase_empty_string(self):
        """
        Test that paraphrasing an empty string returns an empty string.
        """
        original_sentence = ""
        paraphrased_sentence = paraphrase(original_sentence)
        self.assertEqual(original_sentence, paraphrased_sentence, "Paraphrasing an empty string should return an empty string.")
        self.assertIsInstance(paraphrased_sentence, str)

    def test_paraphrase_single_word_no_synonym(self):
        """
        Test paraphrasing a single word that is unlikely to have common synonyms.
        Expecting it to return the original word.
        """
        original_word = "qwertyuiopasdfghjklzxcvbnm"
        paraphrased_word = paraphrase(original_word)
        self.assertEqual(original_word, paraphrased_word, "Paraphrasing a word with no synonyms should return the original word.")

    def test_paraphrase_sentence_structure_maintained(self):
        """
        Test that the basic sentence structure (number of words) is roughly maintained.
        """
        original_sentence = "This is a test sentence."
        paraphrased_sentence = paraphrase(original_sentence)
        self.assertEqual(len(original_sentence.split()), len(paraphrased_sentence.split()), "Word count should ideally remain the same.")

if __name__ == '__main__':
    unittest.main()
