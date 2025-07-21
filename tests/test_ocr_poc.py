import unittest
import os
import shutil
import csv
from unittest.mock import patch, MagicMock
from src.ocr_poc import pdf_to_images, run_ocr
from scripts.calculate_cer import calculate_cer
from scripts.calculate_iou import calculate_iou
from scripts.fine_tune_lora import fine_tune_lora
from scripts.evaluate_accuracy import evaluate_accuracy

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

    def test_calculate_iou(self):
        """Test the calculate_iou function."""
        # Test case 1: Perfect overlap
        box1 = [0, 0, 10, 10]
        box2 = [0, 0, 10, 10]
        self.assertEqual(calculate_iou(box1, box2), 1.0)

        # Test case 2: No overlap
        box1 = [0, 0, 10, 10]
        box2 = [11, 11, 20, 20]
        self.assertEqual(calculate_iou(box1, box2), 0.0)

        # Test case 3: Partial overlap
        box1 = [0, 0, 10, 10]
        box2 = [5, 5, 15, 15]
        self.assertAlmostEqual(calculate_iou(box1, box2), 0.14285714285714285)

        # Test case 4: One box inside another
        box1 = [0, 0, 20, 20]
        box2 = [5, 5, 15, 15]
        self.assertAlmostEqual(calculate_iou(box1, box2), 0.25)

        # Test case 5: Touching edges (no overlap area)
        box1 = [0, 0, 10, 10]
        box2 = [10, 0, 20, 10]
        self.assertEqual(calculate_iou(box1, box2), 0.0)

    @patch('src.ocr_poc.PaddleOCR')
    def test_lora_model_loading(self, MockPaddleOCR):
        """Test that the LoRA model path is correctly passed and used."""
        mock_ocr_instance = MockPaddleOCR.return_value
        mock_result = [[[[[10, 10], [100, 10], [100, 30], [10, 30]], ('lora text', 0.99)]]]
        mock_ocr_instance.ocr.return_value = mock_result

        lora_model_dir = "tests/output/lora_model"
        os.makedirs(lora_model_dir)

        image_paths = [os.path.join(self.output_folder, "page_1.png")]
        with open(image_paths[0], 'w') as f:
            f.write('')

        # Run OCR with the lora_path argument
        run_ocr(image_paths, self.output_csv_path, lora_path=lora_model_dir)

        # Check if PaddleOCR was initialized with the correct directory
        # The first call is the standard engine, the second is the placeholder, the third is LoRA
        # We check the arguments of the third call to PaddleOCR
        self.assertEqual(MockPaddleOCR.call_args_list[2][1]['rec_model_dir'], lora_model_dir)

    def test_fine_tune_lora_script(self):
        """Test the fine_tune_lora script simulation."""
        dataset_path = "tests/dummy_dataset"
        output_path = "tests/output/fine_tuned_model"
        os.makedirs(dataset_path, exist_ok=True)

        fine_tune_lora(dataset_path, output_path, epochs=1, learning_rate=0.001)

        # Check if the simulated model file was created
        self.assertTrue(os.path.exists(os.path.join(output_path, "lora_model_weights.pdparams")))

    def test_evaluate_accuracy_script(self):
        """Test the evaluate_accuracy script."""
        # Create dummy ocr results and ground truth files
        with open(self.output_csv_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['page', 'block_id', 'x0', 'y0', 'x1', 'y1', 'text', 'confidence'])
            writer.writerow([1, 0, 10, 10, 100, 30, 'hello', 0.99])

        with open(self.ground_truth_txt_path, 'w', encoding='utf-8') as f:
            f.write('jello')

        # Redirect stdout to check the output of the script
        from io import StringIO
        import sys
        captured_output = StringIO()
        sys.stdout = captured_output

        evaluate_accuracy(self.output_csv_path, self.ground_truth_txt_path)

        sys.stdout = sys.__stdout__  # Reset stdout

        # Check the output
        output = captured_output.getvalue()
        self.assertIn("Character Error Rate (CER)", output)
        self.assertIn("0.2000", output) # CER for 'hello' vs 'jello' is 1/5 = 0.2

if __name__ == '__main__':
    unittest.main()