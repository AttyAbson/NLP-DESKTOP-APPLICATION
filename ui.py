from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTextEdit, QLabel, QFileDialog, QDialog, QSplitter, QFrame, QProgressBar,
    QMessageBox, QLineEdit, QApplication
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPalette, QColor
from sentiment_analyzer import SentimentAnalyzer
from spam_detector import SpamDetector
from web_scraper import WebScraper
import sys

class ResultWindow(QDialog):
    def __init__(self, title, result, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(600, 400)
        
        # Styling
        self.setStyleSheet("""
            QDialog {
                background-color: #2c3e50;
                color: #ecf0f1;
                font-family: 'Segoe UI';
            }
            QLabel {
                font-size: 14px;
                padding: 10px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        layout = QVBoxLayout()
        
        # Result display with styling
        result_frame = QFrame()
        result_frame.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        frame_layout = QVBoxLayout(result_frame)
        self.result_label = QLabel(result)
        self.result_label.setWordWrap(True)
        self.result_label.setFont(QFont("Segoe UI", 12))
        self.result_label.setOpenExternalLinks(True)
        frame_layout.addWidget(self.result_label)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.setMinimumHeight(40)
        
        layout.addWidget(result_frame, 1)
        layout.addWidget(close_btn)
        close_btn.clicked.connect(self.close)
        self.setLayout(layout)

class InputWindow(QDialog):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(700, 500)
        
        # Modern styling
        self.setStyleSheet("""
            QDialog {
                background-color: #2c3e50;
                color: #ecf0f1;
                font-family: 'Segoe UI';
            }
            QTextEdit {
                background-color: #34495e;
                color: #ecf0f1;
                border: 1px solid #7f8c8d;
                border-radius: 4px;
                padding: 8px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QLabel {
                font-size: 14px;
            }
        """)
        
        main_layout = QVBoxLayout()
        
        # Text input area
        input_layout = QVBoxLayout()
        input_layout.addWidget(QLabel("Enter text or upload a file:"))
        
        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("Type or paste your text here...")
        input_layout.addWidget(self.text_edit, 1)
        
        # Button layout
        button_layout = QHBoxLayout()
        self.upload_btn = QPushButton("📁 Upload Text File")
        self.submit_btn = QPushButton("✅ Submit")
        self.cancel_btn = QPushButton("❌ Cancel")
        
        button_layout.addWidget(self.upload_btn)
        button_layout.addWidget(self.submit_btn)
        button_layout.addWidget(self.cancel_btn)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate mode
        self.progress_bar.setVisible(False)
        
        main_layout.addLayout(input_layout, 1)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.progress_bar)
        
        # Connect signals
        self.upload_btn.clicked.connect(self.upload_file)
        self.submit_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        
        self.setLayout(main_layout)

    def upload_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open Text File", "", "Text Files (*.txt);;All Files (*)"
        )
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    self.text_edit.setText(file.read())
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to read file: {str(e)}")
                
    def show_processing(self):
        self.progress_bar.setVisible(True)
        self.submit_btn.setEnabled(False)
        self.upload_btn.setEnabled(False)
        
    def hide_processing(self):
        self.progress_bar.setVisible(False)
        self.submit_btn.setEnabled(True)
        self.upload_btn.setEnabled(True)

class WebScraperDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Web Scraper")
        self.setMinimumSize(700, 500)
        
        self.setStyleSheet("""
            QDialog {
                background-color: #2c3e50;
                color: #ecf0f1;
                font-family: 'Segoe UI';
            }
            QLabel, QLineEdit, QTextEdit, QPushButton {
                font-size: 14px;
            }
            QLineEdit, QTextEdit {
                background-color: #34495e;
                color: #ecf0f1;
                border: 1px solid #7f8c8d;
                border-radius: 4px;
                padding: 8px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton#scrapeBtn {
                background-color: #9b59b6;
            }
            QPushButton#scrapeBtn:hover {
                background-color: #8e44ad;
            }
            QPushButton#sentimentBtn {
                background-color: #27ae60;
            }
            QPushButton#sentimentBtn:hover {
                background-color: #219653;
            }
            QPushButton#spamBtn {
                background-color: #e74c3c;
            }
            QPushButton#spamBtn:hover {
                background-color: #c0392b;
            }
        """)
        
        layout = QVBoxLayout()
        
        # URL input
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("Enter URL:"))
        self.url_edit = QLineEdit()
        self.url_edit.setPlaceholderText("https://example.com/article")
        url_layout.addWidget(self.url_edit, 1)
        
        # Scrape button
        self.scrape_btn = QPushButton("🌐 Scrape Article")
        self.scrape_btn.setObjectName("scrapeBtn")
        url_layout.addWidget(self.scrape_btn)
        
        # Article display
        self.article_edit = QTextEdit()
        self.article_edit.setReadOnly(True)
        self.article_edit.setPlaceholderText("Scraped content will appear here...")
        
        # Action buttons
        button_layout = QHBoxLayout()
        self.analyze_sentiment_btn = QPushButton("📊 Analyze Sentiment")
        self.analyze_sentiment_btn.setObjectName("sentimentBtn")
        self.analyze_spam_btn = QPushButton("🚫 Detect Spam")
        self.analyze_spam_btn.setObjectName("spamBtn")
        self.copy_btn = QPushButton("📋 Copy to Clipboard")
        self.close_btn = QPushButton("❌ Close")
        
        button_layout.addWidget(self.analyze_sentiment_btn)
        button_layout.addWidget(self.analyze_spam_btn)
        button_layout.addWidget(self.copy_btn)
        button_layout.addWidget(self.close_btn)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setVisible(False)
        
        layout.addLayout(url_layout)
        layout.addWidget(self.article_edit, 1)
        layout.addLayout(button_layout)
        layout.addWidget(self.progress_bar)
        
        self.setLayout(layout)
        
        # Connect signals
        self.scrape_btn.clicked.connect(self.scrape_article)
        self.analyze_sentiment_btn.clicked.connect(self.analyze_sentiment)
        self.analyze_spam_btn.clicked.connect(self.analyze_spam)
        self.copy_btn.clicked.connect(self.copy_to_clipboard)
        self.close_btn.clicked.connect(self.close)
    
    def scrape_article(self):
        url = self.url_edit.text().strip()
        if not url:
            QMessageBox.warning(self, "Warning", "Please enter a URL.")
            return
            
        self.progress_bar.setVisible(True)
        self.scrape_btn.setEnabled(False)
        
        # Use QTimer to run the scraping in the background to avoid freezing the UI
        QTimer.singleShot(50, lambda: self.perform_scraping(url))
    
    def perform_scraping(self, url):
        try:
            scraper = WebScraper()
            article_text = scraper.scrape_article(url)
            self.article_edit.setText(article_text)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Scraping failed: {str(e)}")
        finally:
            self.progress_bar.setVisible(False)
            self.scrape_btn.setEnabled(True)
    
    def analyze_sentiment(self):
        article_text = self.article_edit.toPlainText()
        if article_text and not article_text.startswith("Error") and not article_text.startswith("Invalid"):
            self.accept()
            self.parent().process_sentiment_from_scraper(article_text)
    
    def analyze_spam(self):
        article_text = self.article_edit.toPlainText()
        if article_text and not article_text.startswith("Error") and not article_text.startswith("Invalid"):
            self.accept()
            self.parent().process_spam_from_scraper(article_text)
    
    def copy_to_clipboard(self):
        text = self.article_edit.toPlainText()
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            QMessageBox.information(self, "Copied", "Article text copied to clipboard!")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Text Analysis Toolkit")
        self.setMinimumSize(900, 700)
        
        # Modern styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2c3e50;
                color: #ecf0f1;
                font-family: 'Segoe UI';
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 15px 25px;
                font-size: 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton#sentimentBtn {
                background-color: #27ae60;
            }
            QPushButton#sentimentBtn:hover {
                background-color: #219653;
            }
            QPushButton#spamBtn {
                background-color: #e74c3c;
            }
            QPushButton#spamBtn:hover {
                background-color: #c0392b;
            }
            QPushButton#scrapeBtn {
                background-color: #9b59b6;
            }
            QPushButton#scrapeBtn:hover {
                background-color: #8e44ad;
            }
            QLabel {
                font-size: 14px;
            }
            QSplitter::handle {
                background-color: #34495e;
            }
            QProgressBar {
                background-color: #34495e;
                color: #ecf0f1;
                border: 1px solid #7f8c8d;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 4px;
            }
        """)
        
        # Create central widget and main layout
        central_widget = QWidget()
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Title label
        title_label = QLabel("<h1 style='text-align:center;color:#3498db;'>Text Analysis Toolkit</h1>")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # Create splitter for side-by-side preview
        splitter = QSplitter(Qt.Horizontal)
        splitter.setHandleWidth(10)
        
        # Sentiment preview panel
        sentiment_frame = QFrame()
        sentiment_frame.setFrameShape(QFrame.StyledPanel)
        sentiment_layout = QVBoxLayout(sentiment_frame)
        sentiment_layout.setSpacing(10)
        sentiment_layout.setContentsMargins(15, 15, 15, 15)
        
        sentiment_title = QLabel("<h2 style='color:#27ae60;'>Sentiment Analysis</h2>")
        sentiment_title.setAlignment(Qt.AlignCenter)
        sentiment_layout.addWidget(sentiment_title)
        
        self.sentiment_preview = QLabel("No analysis performed yet")
        self.sentiment_preview.setWordWrap(True)
        self.sentiment_preview.setStyleSheet("""
            QLabel {
                background-color: #34495e;
                padding: 15px;
                border-radius: 8px;
                min-height: 200px;
                font-size: 14px;
            }
        """)
        sentiment_layout.addWidget(self.sentiment_preview, 1)
        
        # Spam preview panel
        spam_frame = QFrame()
        spam_frame.setFrameShape(QFrame.StyledPanel)
        spam_layout = QVBoxLayout(spam_frame)
        spam_layout.setSpacing(10)
        spam_layout.setContentsMargins(15, 15, 15, 15)
        
        spam_title = QLabel("<h2 style='color:#e74c3c;'>Spam Detection</h2>")
        spam_title.setAlignment(Qt.AlignCenter)
        spam_layout.addWidget(spam_title)
        
        self.spam_preview = QLabel("No analysis performed yet")
        self.spam_preview.setWordWrap(True)
        self.spam_preview.setStyleSheet("""
            QLabel {
                background-color: #34495e;
                padding: 15px;
                border-radius: 8px;
                min-height: 200px;
                font-size: 14px;
            }
        """)
        spam_layout.addWidget(self.spam_preview, 1)
        
        # Add frames to splitter
        splitter.addWidget(sentiment_frame)
        splitter.addWidget(spam_frame)
        splitter.setSizes([400, 400])
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(30)
        self.sentiment_btn = QPushButton("📊 Analyze Sentiment")
        self.sentiment_btn.setObjectName("sentimentBtn")
        self.sentiment_btn.setMinimumHeight(50)
        
        self.spam_btn = QPushButton("🚫 Detect Spam")
        self.spam_btn.setObjectName("spamBtn")
        self.spam_btn.setMinimumHeight(50)
        
        self.scrape_btn = QPushButton("🌐 Scrape Web Article")
        self.scrape_btn.setObjectName("scrapeBtn")
        self.scrape_btn.setMinimumHeight(50)
        
        button_layout.addWidget(self.sentiment_btn)
        button_layout.addWidget(self.spam_btn)
        button_layout.addWidget(self.scrape_btn)
        
        # Status label
        self.status_label = QLabel("Ready")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("font-size: 12px; color: #95a5a6;")
        
        # Add widgets to main layout
        main_layout.addWidget(splitter, 1)
        main_layout.addLayout(button_layout)
        main_layout.addWidget(self.status_label)
        
        self.setCentralWidget(central_widget)
        
        # Initialize analyzers
        self.sentiment_analyzer = SentimentAnalyzer()
        self.spam_detector = SpamDetector()
        self.web_scraper = WebScraper()
        
        # Connect signals
        self.sentiment_btn.clicked.connect(self.run_sentiment_analysis)
        self.spam_btn.clicked.connect(self.run_spam_detection)
        self.scrape_btn.clicked.connect(self.open_web_scraper)

    def run_sentiment_analysis(self):
        input_dialog = InputWindow("Sentiment Analysis Input", self)
        if input_dialog.exec_() == QDialog.Accepted:
            text = input_dialog.text_edit.toPlainText()
            if text:
                input_dialog.show_processing()
                self.status_label.setText("Analyzing sentiment...")
                QTimer.singleShot(50, lambda: self.process_sentiment(text, input_dialog))

    def process_sentiment(self, text, dialog):
        try:
            sentiment = self.sentiment_analyzer.analyze(text)
            color = self.get_sentiment_color(sentiment)
            
            # Extract confidence score from result string
            confidence = "0.00"
            if '(' in sentiment:
                confidence = sentiment.split('(')[1].split(')')[0]
            
            result_text = f"""
                <b>Text Preview:</b> {text[:200]}...<br><br>
                <b>Sentiment:</b> <span style='color:{color};font-size:14px;'>{sentiment.split('(')[0].strip()}</span><br>
                <b>Confidence:</b> {confidence}
            """
            self.sentiment_preview.setText(result_text)
            
            # Show detailed result
            result_window = ResultWindow(
                "Sentiment Analysis Result", 
                f"""
                <b>Analyzed Text:</b><br>
                <div style='background-color:#34495e; padding:10px; border-radius:5px; margin-bottom:15px;'>
                    {text}
                </div>
                <b>Sentiment:</b> <span style='color:{color};font-size:16px;'>{sentiment.split('(')[0].strip()}</span><br>
                <b>Confidence:</b> {confidence}
                """,
                self
            )
            result_window.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Analysis failed: {str(e)}")
        finally:
            dialog.hide_processing()
            self.status_label.setText("Analysis complete")
            
    def get_sentiment_color(self, sentiment):
        if "Positive" in sentiment:
            return "#2ecc71"
        elif "Negative" in sentiment:
            return "#e74c3c"
        else:
            return "#f39c12"

    def run_spam_detection(self):
        input_dialog = InputWindow("Spam Detection Input", self)
        if input_dialog.exec_() == QDialog.Accepted:
            text = input_dialog.text_edit.toPlainText()
            if text:
                input_dialog.show_processing()
                self.status_label.setText("Detecting spam...")
                QTimer.singleShot(50, lambda: self.process_spam(text, input_dialog))

    def process_spam(self, text, dialog):
        try:
            is_spam, confidence = self.spam_detector.detect(text)
            result = "SPAM 🚫" if is_spam else "Not Spam ✅"
            color = "#e74c3c" if is_spam else "#2ecc71"
            
            result_text = f"""
                <b>Text Preview:</b> {text[:200]}...<br><br>
                <b>Result:</b> <span style='color:{color};font-size:14px;'>{result}</span><br>
                <b>Confidence:</b> {confidence:.2f}
            """
            self.spam_preview.setText(result_text)
            
            # Show detailed result
            result_window = ResultWindow(
                "Spam Detection Result", 
                f"""
                <b>Analyzed Text:</b><br>
                <div style='background-color:#34495e; padding:10px; border-radius:5px; margin-bottom:15px;'>
                    {text}
                </div>
                <b>Result:</b> <span style='color:{color};font-size:16px;'>{result}</span><br>
                <b>Confidence:</b> {confidence:.2f}
                """,
                self
            )
            result_window.exec_()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Detection failed: {str(e)}")
        finally:
            dialog.hide_processing()
            self.status_label.setText("Detection complete")
    
    def open_web_scraper(self):
        scraper_dialog = WebScraperDialog(self)
        scraper_dialog.exec_()
    
    def process_sentiment_from_scraper(self, text):
        # Reuse existing sentiment processing
        self.run_sentiment_analysis_from_text(text)
    
    def process_spam_from_scraper(self, text):
        # Reuse existing spam processing
        self.run_spam_detection_from_text(text)
    
    def run_sentiment_analysis_from_text(self, text):
        input_dialog = InputWindow("Sentiment Analysis Input", self)
        input_dialog.text_edit.setText(text)
        input_dialog.show_processing()
        self.status_label.setText("Analyzing sentiment...")
        QTimer.singleShot(50, lambda: self.process_sentiment(text, input_dialog))
    
    def run_spam_detection_from_text(self, text):
        input_dialog = InputWindow("Spam Detection Input", self)
        input_dialog.text_edit.setText(text)
        input_dialog.show_processing()
        self.status_label.setText("Detecting spam...")
        QTimer.singleShot(50, lambda: self.process_spam(text, input_dialog))

def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle("Fusion")
    
    # Create palette for dark theme
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(44, 62, 80))
    palette.setColor(QPalette.WindowText, QColor(236, 240, 241))
    palette.setColor(QPalette.Base, QColor(52, 73, 94))
    palette.setColor(QPalette.AlternateBase, QColor(44, 62, 80))
    palette.setColor(QPalette.ToolTipBase, QColor(236, 240, 241))
    palette.setColor(QPalette.ToolTipText, QColor(236, 240, 241))
    palette.setColor(QPalette.Text, QColor(236, 240, 241))
    palette.setColor(QPalette.Button, QColor(52, 152, 219))
    palette.setColor(QPalette.ButtonText, QColor(236, 240, 241))
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Highlight, QColor(155, 89, 182))
    palette.setColor(QPalette.HighlightedText, Qt.black)
    app.setPalette(palette)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()