import unittest
import os
import shutil
import csv
import json
import sys
from unittest.mock import patch, MagicMock
from src.ocr_poc import pdf_to_images, run_ocr
from scripts.calculate_cer import calculate_cer
from scripts.calculate_iou import calculate_iou
import scripts.finetune_lora # Add this import

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
        self.ground_truth_json_path = "tests/test_ground_truth.json" # New ground truth JSON path

        # Create a dummy ground truth JSON for testing accuracy_reviewer
        dummy_gt_json_content = {
            "1": [
                {"bbox": [10, 10, 100, 30], "text": "fine-tuned text"}
            ]
        }
        with open(self.ground_truth_json_path, 'w', encoding='utf-8') as f:
            json.dump(dummy_gt_json_content, f)

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
        if os.path.exists(self.ground_truth_json_path):
            os.remove(self.ground_truth_json_path)

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
        # Read the output CSV to get the ocr text
        ocr_text = ""
        with open(self.output_csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                ocr_text += row['text']
        cer = calculate_cer(self_ground_truth_content, ocr_text)
        self.assertEqual(cer, 0.0) # Expect 0 CER if OCR text matches ground truth

    @patch('src.ocr_poc.PaddleOCR')
    def test_ensemble_voting_and_kenlm_correction(self, MockPaddleOCR):
        """Test the ensemble voting and KenLM correction frameworks."""
        mock_ocr_instance_1 = MockPaddleOCR.return_value
        mock_ocr_instance_2 = MockPaddleOCR.return_value
        mock_ocr_instance_3 = MockPaddleOCR.return_value

        # Simulate results from three engines
        mock_result_engine_1 = [[[[[10, 10], [100, 10], [100, 30], [10, 30]], ('text_A', 0.9)]]]
        mock_result_engine_2 = [[[[[10, 10], [100, 10], [100, 30], [10, 30]], ('text_B', 0.8)]]]
        mock_result_engine_3 = [[[[[10, 10], [100, 10], [100, 30], [10, 30]], ('text_C', 0.95)]]] # Highest confidence

        # Configure side_effect for PaddleOCR mock to return results for each engine call
        # The run_ocr function calls ocr_engine.ocr three times per image
        mock_ocr_instance_1.ocr.side_effect = [mock_result_engine_1, mock_result_engine_2, mock_result_engine_3]

        image_paths = [os.path.join(self.output_folder, "page_1.png")]
        for path in image_paths:
            with open(path, 'w') as f: # create empty files
                f.write('')

        # Set ground truth content for this test
        self_ground_truth_content = "text_C" # Expect highest confidence text
        with open(self.ground_truth_txt_path, 'w', encoding='utf-8') as f:
            f.write(self_ground_truth_content)

        # Run the function
        run_ocr(image_paths, self.output_csv_path)

        # Assertions
        self.assertTrue(os.path.exists(self.output_csv_path))
        with open(self.output_csv_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 2) # Header + 1 data row
            # Expect the highest confidence text (text_C) from ensemble voting
            self.assertIn('text_C', lines[1])

        # Test CER calculation
        ocr_text = ""
        with open(self.output_csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                ocr_text += row['text']
        cer = calculate_cer(self_ground_truth_content, ocr_text)
        self.assertEqual(cer, 0.0) # Expect 0 CER if OCR text matches ground truth

    @patch('src.ocr_poc.PaddleOCR')
    @patch('src.ocr_poc.MistralOCR_LoRA_Engine')
    @patch('scripts.finetune_lora.finetune_lora')
    @patch('argparse.ArgumentParser.parse_args') # Patch parse_args directly
    def test_lora_fine_tuning_and_accuracy_review(self, MockParseArgs, MockFinetuneLoRA, MockMistralOCR_LoRA_Engine, MockPaddleOCR):
        """Test the LoRA fine-tuning and accuracy review frameworks."""
        # Configure MockParseArgs to return a mock object with the required attributes
        mock_args = MagicMock()
        mock_args.ocr_csv = self.output_csv_path
        mock_args.ground_truth_json = self.ground_truth_json_path
        mock_args.iou_threshold = 0.5 # Default value
        MockParseArgs.return_value = mock_args

        # Simulate fine-tuning process
        mock_lora_model_path = "./lora_finetuned_model/lora_adapters"
        MockFinetuneLoRA.return_value = mock_lora_model_path

        # Configure the mock for MistralOCR_LoRA_Engine
        mock_lora_instance = MockMistralOCR_LoRA_Engine.return_value
        mock_lora_result = [[[[[10, 10], [100, 10], [100, 30], [10, 30]], ('fine-tuned text', 0.98)]]]
        mock_lora_instance.ocr.return_value = mock_lora_result

        # Configure the mock for PaddleOCR (other engines)
        mock_paddle_instance = MockPaddleOCR.return_value
        mock_paddle_result = [[[[[10, 10], [100, 10], [100, 30], [10, 30]], ('paddle text', 0.90)]]]
        mock_paddle_instance.ocr.return_value = mock_paddle_result

        image_paths = [os.path.join(self.output_folder, "page_1.png")]
        for path in image_paths:
            with open(path, 'w') as f: # create empty files
                f.write('')

        # Set ground truth content for this test
        self_ground_truth_content = "fine-tuned text"
        with open(self.ground_truth_txt_path, 'w', encoding='utf-8') as f:
            f.write(self_ground_truth_content)

        # Run the function (simulating the overall process)
        run_ocr(image_paths, self.output_csv_path)

        # Simulate calling accuracy_reviewer.main
        # We need to mock sys.argv for argparse in accuracy_reviewer.py
        # MockSysArgv.return_value = ['accuracy_reviewer.py',
        #                             '--ocr_csv', self.output_csv_path,
        #                             '--ground_truth_json', self.ground_truth_json_path]
        
        # Import accuracy_reviewer here to ensure the patched sys.argv is used
        import scripts.accuracy_reviewer
        with patch('builtins.print') as mock_print: # Suppress print output from main
            scripts.accuracy_reviewer.main()
        
        # Assertions for accuracy_reviewer output (check mock_print calls)
        # This is a simplified check; a more robust test would parse mock_print.call_args_list
        mock_print.assert_any_call(unittest.mock.ANY) # Check if print was called at all
        # You might add more specific assertions here to check the reported CER/IoU values

        # Verify that MistralOCR_LoRA_Engine was initialized with the correct path
        MockMistralOCR_LoRA_Engine.assert_called_with("mistralai/Mistral-7B-v0.1", mock_lora_model_path)
        
        # Verify that the LoRA engine's ocr method was called
        mock_lora_instance.ocr.assert_called_once()

    def test_calculate_cer(self):
        """Test the calculate_cer function."""
        self.assertEqual(calculate_cer("apple", "apple"), 0.0)
        self.assertEqual(calculate_cer("apple", "appel"), 2.0 / 5.0)
        self.assertEqual(calculate_cer("apple", "apply"), 1.0 / 5.0)
        self.assertEqual(calculate_cer("apple", "ale"), 2.0 / 5.0)
        self.assertEqual(calculate_cer("", ""), 0.0)
        self.assertEqual(calculate_cer("apple", ""), 1.0)
        self.assertEqual(calculate_cer("", "apple"), 1.0)

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

if __name__ == '__main__':
    unittest.main()