
import unittest
import os
import shutil
from unittest.mock import patch, MagicMock
from src.ocr_poc import pdf_to_images, run_ocr
from scripts.calculate_cer import calculate_cer

class TestOcrPoc(unittest.TestCase):

    def setUp(self):
        self.test_pdf_path = "tests/test.pdf"
        self.ground_truth_txt_path = "tests/test.txt"
        # Restore original ground truth content for other tests
        original_ground_truth_content = "精度"
        with open(self.ground_truth_txt_path, 'w', encoding='utf-8') as f:
            f.write(original_ground_truth_content)

        self.output_folder = "tests/output/temp_images"
        self.output_csv_path = "tests/output/test_ocr_results.csv"
        # Ensure the output directory is clean before each test
        if os.path.exists("tests/output"):
            shutil.rmtree("tests/output")
        os.makedirs(self.output_folder)

    def tearDown(self):
        # Clean up created files and directories
        if os.path.exists("tests/output"):
            shutil.rmtree("tests/output")
        # Restore original ground truth content
        original_ground_truth_content = "精度"
        with open(self.ground_truth_txt_path, 'w', encoding='utf-8') as f:
            f.write(original_ground_truth_content)

    def test_pdf_to_images(self):
        """Test that PDF pages are converted to images."""
        image_paths = pdf_to_images(self.test_pdf_path, self.output_folder)
        # The test.pdf has 2 pages
        self.assertEqual(len(image_paths), 2)
        for path in image_paths:
            self.assertTrue(os.path.exists(path))

    @patch('src.ocr_poc.PaddleOCR')
    def test_run_ocr_with_mock(self, MockPaddleOCR):
        """Test the OCR process and CSV output using a mock."""
        # Configure the mock to return a predictable result
        mock_ocr_instance = MockPaddleOCR.return_value
        mock_result = [[[[[10, 10], [100, 10], [100, 30], [10, 30]], ('mocked text', 0.99)]]]
        mock_ocr_instance.ocr.return_value = mock_result

        # Create some dummy image paths for the test
        image_paths = [os.path.join(self.output_folder, "page_1.png"),
                       os.path.join(self.output_folder, "page_2.png")]
        for path in image_paths:
            with open(path, 'w') as f: # create empty files
                f.write('')

        # Set ground truth content for this test
        self_ground_truth_content = "mocked text" * len(image_paths)
        with open(self.ground_truth_txt_path, 'w', encoding='utf-8') as f:
            f.write(self_ground_truth_content)

        # Run the function
        run_ocr(image_paths, self.output_csv_path)

        # Assertions
        self.assertTrue(os.path.exists(self.output_csv_path))
        with open(self.output_csv_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 3) # Header + 2 mocked data rows
            self.assertEqual(lines[0].strip(), 'page,block_id,x0,y0,x1,y1,text,confidence')
            self.assertIn('mocked text', lines[1])

        # Test CER calculation
        cer = calculate_cer(self.output_csv_path, self.ground_truth_txt_path)
        self.assertEqual(cer, 0.0) # Expect 0 CER if OCR text matches ground truth

if __name__ == '__main__':
    unittest.main()
