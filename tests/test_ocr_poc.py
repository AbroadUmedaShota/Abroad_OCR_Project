
import unittest
import os
import subprocess
import csv
import zipfile

class TestOcrPoc(unittest.TestCase):
    TEST_PDF_PATH = "tests/test.pdf"
    OUTPUT_CSV_NAME = "test.pdf_ocr_results.csv"
    OUTPUT_ZIP_NAME = "test.zip"

    @classmethod
    def setUpClass(cls):
        # Ensure test.pdf exists
        if not os.path.exists(cls.TEST_PDF_PATH):
            # Create a dummy PDF for testing if it doesn't exist
            # In a real scenario, this would be a proper test PDF
            with open(cls.TEST_PDF_PATH, "w") as f:
                f.write("This is a dummy PDF content.")

    def tearDown(self):
        # Clean up generated files after each test
        if os.path.exists(self.OUTPUT_CSV_NAME):
            os.remove(self.OUTPUT_CSV_NAME)
        if os.path.exists(self.OUTPUT_ZIP_NAME):
            os.remove(self.OUTPUT_ZIP_NAME)
        # Clean up temp_images folder if created
        if os.path.exists("temp_images"):
            for f in os.listdir("temp_images"):
                os.remove(os.path.join("temp_images", f))
            os.rmdir("temp_images")

    def test_cli_execution_and_csv_output(self):
        # Run the OCR PoC script via CLI
        command = ["python", "src/ocr_poc.py", self.TEST_PDF_PATH]
        result = subprocess.run(command, capture_output=True, text=True, cwd=os.getcwd())

        self.assertEqual(result.returncode, 0, f"CLI execution failed: {result.stderr}")
        self.assertTrue(os.path.exists(self.OUTPUT_CSV_NAME), "OCR results CSV not generated.")

        # Verify CSV content
        with open(self.OUTPUT_CSV_NAME, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            fieldnames = reader.fieldnames
            expected_fieldnames = ['page', 'block_id', 'x0', 'y0', 'x1', 'y1', 'text', 'confidence']
            self.assertEqual(fieldnames, expected_fieldnames, "CSV headers do not match expected.")
            
            # Check if there's at least one row (assuming dummy PDF will produce some output)
            rows = list(reader)
            self.assertGreater(len(rows), 0, "No data rows found in CSV.")
            
            # Basic check for data types (assuming first row is representative)
            if rows:
                first_row = rows[0]
                self.assertIn('page', first_row)
                self.assertIn('block_id', first_row)
                self.assertIn('x0', first_row)
                self.assertIn('y0', first_row)
                self.assertIn('x1', first_row)
                self.assertIn('y1', first_row)
                self.assertIn('text', first_row)
                self.assertIn('confidence', first_row)
                
                self.assertIsInstance(int(first_row['page']), int)
                self.assertIsInstance(int(first_row['block_id']), int)
                self.assertIsInstance(float(first_row['x0']), float)
                self.assertIsInstance(float(first_row['y0']), float)
                self.assertIsInstance(float(first_row['x1']), float)
                self.assertIsInstance(float(first_row['y1']), float)
                self.assertIsInstance(first_row['text'], str)
                self.assertIsInstance(float(first_row['confidence']), float)

    def test_zip_output(self):
        # Run the OCR PoC script with --zip option
        command = ["python", "src/ocr_poc.py", self.TEST_PDF_PATH, "--zip"]
        result = subprocess.run(command, capture_output=True, text=True, cwd=os.getcwd())

        self.assertEqual(result.returncode, 0, f"CLI execution with --zip failed: {result.stderr}")
        self.assertTrue(os.path.exists(self.OUTPUT_ZIP_NAME), "ZIP file not generated.")

        # Verify ZIP content (at least PDF and CSV are inside)
        with zipfile.ZipFile(self.OUTPUT_ZIP_NAME, 'r') as zf:
            self.assertIn(os.path.basename(self.TEST_PDF_PATH), zf.namelist(), "Original PDF not in ZIP.")
            self.assertIn(self.OUTPUT_CSV_NAME, zf.namelist(), "OCR results CSV not in ZIP.")

if __name__ == '__main__':
    unittest.main()
