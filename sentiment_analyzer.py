from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np

"""
Advanced Sentiment Analyzer using state-of-the-art models
"""

class SentimentAnalyzer:
    def __init__(self):
        # Try multiple advanced models in order of preference
        models_to_try = [
            "j-hartmann/emotion-english-distilroberta-base",  # Emotion detection model
            "SamLowe/roberta-base-go_emotions",  # Google's Go Emotions dataset
            "michellejieli/emotion_text_classifier",  # Multi-emotion classifier
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
                
                # Determine model type for proper output interpretation
                if "emotion" in model_name:
                    self.model_type = "emotion"
                elif "go_emotions" in model_name:
                    self.model_type = "go_emotions"
                else:
                    self.model_type = "standard"
                
                print(f"Successfully loaded sentiment model: {model_name}")
                break
            except Exception as e:
                print(f"Failed to load {model_name}: {e}")
                continue
        
        if not self.model_loaded:
            print("All advanced models failed. Using basic pipeline.")
            try:
                self.classifier = pipeline("sentiment-analysis", model="facebook/bart-large-mnli")
                self.model_type = "mnli"
                self.model_loaded = True
            except:
                self.classifier = pipeline("sentiment-analysis")
                self.model_type = "basic"
                self.model_loaded = True

    def analyze(self, text):
        if not self.model_loaded:
            return "Error: No model loaded"
        
        try:
            # Process text in chunks if too long
            max_length = 512
            if len(text) > max_length:
                chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
                results = [self.classifier(chunk) for chunk in chunks]
                
                # Flatten results if nested
                flattened_results = []
                for result in results:
                    if isinstance(result, list) and len(result) > 0:
                        flattened_results.append(result[0])
                    else:
                        flattened_results.append(result)
                
                return self._aggregate_emotion_results(flattened_results)
            else:
                result = self.classifier(text)
                if isinstance(result, list) and len(result) > 0:
                    result = result[0]
                return self._interpret_single_result(result)
                
        except Exception as e:
            return f"Analysis Error: {str(e)}"

    def _aggregate_emotion_results(self, results):
        """Aggregate results from multiple chunks"""
        try:
            if self.model_type == "emotion":
                # Aggregate emotion scores
                emotion_scores = {}
                for result in results:
                    label = result['label'].lower()
                    score = result['score']
                    
                    if label in emotion_scores:
                        emotion_scores[label].append(score)
                    else:
                        emotion_scores[label] = [score]
                
                # Calculate average scores
                avg_emotions = {}
                for emotion, scores in emotion_scores.items():
                    avg_emotions[emotion] = np.mean(scores)
                
                # Find dominant emotion
                dominant_emotion = max(avg_emotions, key=avg_emotions.get)
                confidence = avg_emotions[dominant_emotion]
                
                return self._emotion_to_sentiment(dominant_emotion, confidence)
                
            elif self.model_type == "go_emotions":
                # Handle Go Emotions format
                emotion_counts = {}
                total_confidence = 0
                
                for result in results:
                    label = result['label'].lower()
                    score = result['score']
                    
                    if label in emotion_counts:
                        emotion_counts[label] += score
                    else:
                        emotion_counts[label] = score
                    total_confidence += score
                
                # Normalize and find dominant
                if total_confidence > 0:
                    for emotion in emotion_counts:
                        emotion_counts[emotion] /= len(results)
                
                dominant_emotion = max(emotion_counts, key=emotion_counts.get)
                confidence = emotion_counts[dominant_emotion]
                
                return self._emotion_to_sentiment(dominant_emotion, confidence)
            
            else:
                # Standard sentiment aggregation
                pos_scores = []
                neg_scores = []
                
                for result in results:
                    label = result['label'].lower()
                    score = result['score']
                    
                    if 'pos' in label or 'joy' in label or 'happy' in label:
                        pos_scores.append(score)
                    elif 'neg' in label or 'sad' in label or 'anger' in label:
                        neg_scores.append(score)
                
                avg_pos = np.mean(pos_scores) if pos_scores else 0
                avg_neg = np.mean(neg_scores) if neg_scores else 0
                
                if avg_pos > avg_neg and avg_pos > 0.4:
                    return f"Positive 😊 ({avg_pos:.2f})"
                elif avg_neg > avg_pos and avg_neg > 0.4:
                    return f"Negative 😔 ({avg_neg:.2f})"
                else:
                    return f"Neutral 😐 ({max(avg_pos, avg_neg):.2f})"
                    
        except Exception as e:
            return f"Aggregation Error: {str(e)}"

    def _interpret_single_result(self, result):
        """Interpret single result based on model type"""
        try:
            label = result['label'].lower()
            score = result['score']
            
            if self.model_type in ["emotion", "go_emotions"]:
                return self._emotion_to_sentiment(label, score)
            else:
                # Standard sentiment
                if 'pos' in label and score > 0.5:
                    return f"Positive 😊 ({score:.2f})"
                elif 'neg' in label and score > 0.5:
                    return f"Negative 😔 ({score:.2f})"
                else:
                    return f"Neutral 😐 ({score:.2f})"
                    
        except Exception as e:
            return f"Interpretation Error: {str(e)}"

    def _emotion_to_sentiment(self, emotion, confidence):
        """Convert emotion labels to sentiment"""
        emotion = emotion.lower()
        
        # Positive emotions
        positive_emotions = [
            'joy', 'happiness', 'love', 'excitement', 'gratitude', 
            'admiration', 'amusement', 'approval', 'caring', 'desire',
            'optimism', 'pride', 'relief'
        ]
        
        # Negative emotions  
        negative_emotions = [
            'anger', 'sadness', 'fear', 'disgust', 'annoyance',
            'disappointment', 'disapproval', 'embarrassment', 'grief',
            'nervousness', 'remorse', 'confusion'
        ]
        
        # Neutral emotions
        neutral_emotions = [
            'neutral', 'surprise', 'curiosity', 'realization'
        ]
        
        # Determine sentiment category
        if any(pos_emotion in emotion for pos_emotion in positive_emotions):
            emoji = "😊" if emotion == "joy" else "❤️" if emotion == "love" else "😄"
            return f"Positive {emoji} ({emotion.title()}: {confidence:.2f})"
        elif any(neg_emotion in emotion for neg_emotion in negative_emotions):
            emoji = "😢" if emotion == "sadness" else "😠" if emotion == "anger" else "😟"
            return f"Negative {emoji} ({emotion.title()}: {confidence:.2f})"
        else:
            return f"Neutral 😐 ({emotion.title()}: {confidence:.2f})"

    def get_detailed_emotions(self, text):
        """Get detailed emotion breakdown"""
        if not self.model_loaded or self.model_type not in ["emotion", "go_emotions"]:
            return "Detailed emotions not available with current model"
        
        try:
            result = self.classifier(text, return_all_scores=True)
            if isinstance(result, list) and len(result) > 0:
                result = result[0]
            
            # Sort by confidence
            if isinstance(result, list):
                sorted_emotions = sorted(result, key=lambda x: x['score'], reverse=True)
                return sorted_emotions[:5]  # Top 5 emotions
            else:
                return [result]
                
        except Exception as e:
            return f"Error getting detailed emotions: {str(e)}"

    def get_model_info(self):
        """Return information about the loaded model"""
        if self.model_loaded:
            return f"Using model: {self.model_name} (Type: {self.model_type})"
        else:
            return "No model loaded"