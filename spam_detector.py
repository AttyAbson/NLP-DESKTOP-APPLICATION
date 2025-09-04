from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
import re
import string
from collections import Counter

"""
Advanced Spam Detector using multiple detection strategies
"""

class SpamDetector:
    def __init__(self):
       
        models_to_try = [
            "deepset/deberta-v3-base-injection",  # Prompt injection detection
            "ealvaradob/bert-finetuned-phishing",  # Phishing detection
            "Hate-speech-CNERG/dehatebert-mono-english",  # Hate speech detection
        ]
        
        self.model_loaded = False
        self.model_name = None
        self.model_type = None
        
        for model_name in models_to_try:
            try:
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
                self.classifier = pipeline("text-classification", model=self.model, tokenizer=self.tokenizer)
                self.model_name = model_name
                self.model_loaded = True
                
                # Determine model type
                if "injection" in model_name:
                    self.model_type = "injection"
                elif "phishing" in model_name:
                    self.model_type = "phishing"
                elif "hate" in model_name:
                    self.model_type = "hate"
                else:
                    self.model_type = "general"
                
                print(f"Successfully loaded spam detection model: {model_name}")
                break
            except Exception as e:
                print(f"Failed to load {model_name}: {e}")
                continue
        
        if not self.model_loaded:
            print("All advanced models failed. Using enhanced rule-based detection.")

    def detect(self, text):
        # Start with advanced rule-based detection
        rule_spam, rule_confidence, rule_reasons = self.advanced_rule_detection(text)
        
        if not self.model_loaded:
            return rule_spam, rule_confidence, rule_reasons
        
        try:
            # ML model detection
            model_spam, model_confidence = self._ml_detection(text)
            
            # Linguistic analysis
            linguistic_spam, linguistic_confidence = self._linguistic_analysis(text)
            
            # Combine all detection methods
            final_spam, final_confidence = self._combine_results(
                rule_spam, rule_confidence,
                model_spam, model_confidence,
                linguistic_spam, linguistic_confidence
            )
            
            # Combine reasons
            all_reasons = rule_reasons.copy()
            if model_spam:
                all_reasons.append(f"ML Model detected suspicious patterns ({self.model_type})")
            if linguistic_spam:
                all_reasons.append("Linguistic analysis flagged suspicious patterns")
            
            return final_spam, final_confidence, all_reasons
            
        except Exception as e:
            print(f"ML detection error: {e}. Using rule-based detection.")
            return rule_spam, rule_confidence, rule_reasons

    def _ml_detection(self, text):
        """Machine learning based detection"""
        try:
            max_length = 512
            if len(text) > max_length:
                chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
                results = [self.classifier(chunk)[0] for chunk in chunks]
                
                spam_scores = []
                for result in results:
                    score = self._interpret_ml_result(result)
                    spam_scores.append(score)
                
                avg_score = sum(spam_scores) / len(spam_scores)
                is_spam = avg_score > 0.6
                return is_spam, avg_score
            else:
                result = self.classifier(text)[0]
                score = self._interpret_ml_result(result)
                is_spam = score > 0.6
                return is_spam, score
                
        except Exception as e:
            return False, 0.0

    def _interpret_ml_result(self, result):
        """Interpret ML model results based on model type"""
        label = result['label'].lower()
        score = result['score']
        
        if self.model_type == "injection":
            # Injection detection models
            if 'injection' in label or 'positive' in label:
                return score
            else:
                return 1 - score
        elif self.model_type == "phishing":
            # Phishing detection models
            if 'phishing' in label or 'spam' in label or 'malicious' in label:
                return score
            else:
                return 1 - score
        elif self.model_type == "hate":
            # Hate speech models (hate speech often correlates with spam)
            if 'hate' in label or 'offensive' in label or 'toxic' in label:
                return score * 0.7  # Lower weight since not directly spam
            else:
                return (1 - score) * 0.3
        else:
            # Generic classification
            if any(spam_word in label for spam_word in ['spam', 'malicious', 'toxic', 'hate']):
                return score
            else:
                return 1 - score

    def _linguistic_analysis(self, text):
        """Advanced linguistic analysis for spam detection"""
        try:
            score = 0.0
            text_lower = text.lower()
            
            # Character analysis
            char_analysis = self._analyze_characters(text)
            score += char_analysis * 0.3
            
            # Word analysis
            word_analysis = self._analyze_words(text_lower)
            score += word_analysis * 0.4
            
            # Sentence structure analysis
            structure_analysis = self._analyze_structure(text)
            score += structure_analysis * 0.3
            
            is_spam = score > 0.5
            return is_spam, min(score, 1.0)
            
        except Exception as e:
            return False, 0.0

    def _analyze_characters(self, text):
        """Analyze character patterns"""
        if len(text) == 0:
            return 0.0
        
        score = 0.0
        
        # Excessive punctuation
        punct_count = sum(1 for c in text if c in '!?$')
        punct_ratio = punct_count / len(text)
        if punct_ratio > 0.05:
            score += 0.3
        
        # Excessive caps
        caps_count = sum(1 for c in text if c.isupper())
        caps_ratio = caps_count / len(text)
        if caps_ratio > 0.3:
            score += 0.4
        
        # Number density
        num_count = sum(1 for c in text if c.isdigit())
        num_ratio = num_count / len(text)
        if num_ratio > 0.2:
            score += 0.2
        
        # Special characters
        special_chars = set(text) - set(string.ascii_letters + string.digits + string.whitespace + '.,!?')
        if len(special_chars) > 5:
            score += 0.3
        
        return min(score, 1.0)

    def _analyze_words(self, text_lower):
        """Analyze word patterns and vocabulary"""
        words = text_lower.split()
        if len(words) == 0:
            return 0.0
        
        score = 0.0
        
        # Spam vocabulary
        high_spam_words = [
            'urgent', 'immediate', 'act now', 'limited time', 'expires',
            'congratulations', 'winner', 'selected', 'lottery', 'prize',
            'free money', 'easy money', 'guaranteed', 'risk free',
            'click here', 'call now', 'don\'t delay', 'order now'
        ]
        
        medium_spam_words = [
            'offer', 'deal', 'discount', 'save', 'cheap', 'affordable',
            'amazing', 'incredible', 'unbelievable', 'opportunity',
            'income', 'profit', 'earnings', 'commission'
        ]
        
        # Count spam words
        high_spam_count = sum(1 for word in high_spam_words if word in text_lower)
        medium_spam_count = sum(1 for word in medium_spam_words if word in text_lower)
        
        # Score based on spam word density
        total_spam_score = (high_spam_count * 0.1) + (medium_spam_count * 0.05)
        score += min(total_spam_score, 0.6)
        
        # Repetitive words
        word_counts = Counter(words)
        max_count = max(word_counts.values()) if word_counts else 0
        if max_count > 3:
            score += 0.2
        
        # Average word length (very short or very long can be suspicious)
        avg_word_len = sum(len(word) for word in words) / len(words)
        if avg_word_len < 3 or avg_word_len > 12:
            score += 0.15
        
        return min(score, 1.0)

    def _analyze_structure(self, text):
        """Analyze sentence structure and grammar"""
        sentences = re.split(r'[.!?]+', text)
        if len(sentences) == 0:
            return 0.0
        
        score = 0.0
        
        # Very short sentences (often commands)
        short_sentences = [s for s in sentences if len(s.strip().split()) < 4]
        if len(short_sentences) / len(sentences) > 0.5:
            score += 0.3
        
        # Excessive line breaks or formatting
        if text.count('\n') > len(sentences):
            score += 0.2
        
        # URLs and links
        url_pattern = r'https?://[^\s]+|www\.[^\s]+'
        urls = re.findall(url_pattern, text)
        if len(urls) > 2:
            score += 0.4
        elif len(urls) > 0:
            score += 0.2
        
        # Email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if len(emails) > 1:
            score += 0.3
        
        # Phone numbers
        phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        phones = re.findall(phone_pattern, text)
        if len(phones) > 0:
            score += 0.25
        
        return min(score, 1.0)

    def advanced_rule_detection(self, text):
        """Enhanced rule-based detection with detailed reasons"""
        text_lower = text.lower()
        reasons = []
        total_score = 0.0
        
        # Financial scam patterns
        financial_patterns = [
            (r'\$\d+[,.]?\d*\s*(million|billion|thousand)', 'Large money amounts mentioned'),
            (r'bank\s+(account|details|information)', 'Requests banking information'),
            (r'(transfer|send)\s+money', 'Money transfer requests'),
            (r'inheritance|lottery|prize|winner', 'Lottery/inheritance scam indicators'),
            (r'(social security|ssn|credit card)', 'Requests sensitive financial data')
        ]
        
        for pattern, reason in financial_patterns:
            if re.search(pattern, text_lower):
                total_score += 0.25
                reasons.append(reason)
        
        # Urgency indicators
        urgency_words = [
            'urgent', 'immediately', 'asap', 'expires today', 'limited time',
            'act now', 'hurry', 'final notice', 'last chance', 'expires soon'
        ]
        
        urgency_count = sum(1 for word in urgency_words if word in text_lower)
        if urgency_count > 0:
            total_score += urgency_count * 0.1
            reasons.append(f'Urgency indicators detected ({urgency_count} found)')
        
        # Phishing patterns
        phishing_patterns = [
            (r'click\s+(here|link|below)', 'Suspicious click prompts'),
            (r'verify\s+(account|identity|information)', 'Account verification requests'),
            (r'suspended|blocked|frozen', 'Account threat language'),
            (r'update\s+(payment|billing|account)', 'Payment update requests'),
            (r'confirm\s+(identity|account|details)', 'Identity confirmation requests')
        ]
        
        for pattern, reason in phishing_patterns:
            if re.search(pattern, text_lower):
                total_score += 0.2
                reasons.append(reason)
        
        # Excessive formatting
        if text.count('!') > 3:
            total_score += 0.1
            reasons.append('Excessive exclamation marks')
        
        if text.count('$') > 2:
            total_score += 0.15
            reasons.append('Multiple dollar signs')
        
        # Caps analysis
        caps_ratio = sum(1 for c in text if c.isupper()) / len(text) if len(text) > 0 else 0
        if caps_ratio > 0.3:
            total_score += 0.2
            reasons.append('Excessive capital letters')
        
        # Final determination
        is_spam = total_score > 0.4
        confidence = min(total_score, 1.0)
        
        return is_spam, confidence, reasons

    def _combine_results(self, rule_spam, rule_conf, ml_spam, ml_conf, ling_spam, ling_conf):
        """Combine results from different detection methods"""
        # Weighted combination
        rule_weight = 0.4
        ml_weight = 0.4
        ling_weight = 0.2
        
        combined_confidence = (rule_conf * rule_weight + 
                             ml_conf * ml_weight + 
                             ling_conf * ling_weight)
        
        # If any method strongly indicates spam, lean towards spam
        strong_spam_threshold = 0.8
        if (rule_spam and rule_conf > strong_spam_threshold) or \
           (ml_spam and ml_conf > strong_spam_threshold) or \
           (ling_spam and ling_conf > strong_spam_threshold):
            is_spam = True
        else:
            is_spam = combined_confidence > 0.5
        
        return is_spam, combined_confidence

    def get_model_info(self):
        """Return information about the loaded model"""
        if self.model_loaded:
            return f"Using model: {self.model_name} (Type: {self.model_type})"
        else:
            return "Using advanced rule-based detection with linguistic analysis"