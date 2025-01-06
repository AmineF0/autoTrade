# sentiment_analyzer.py
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import pandas as pd
import numpy as np
from typing import List, Dict, Union
from tqdm import tqdm
import logging

class FinancialSentimentAnalyzer:
    """Financial news sentiment analyzer using FinBERT model"""
    
    def __init__(self, batch_size: int = 8, device: str = None):
        """
        Initialize the sentiment analyzer
        
        Args:
            batch_size: Number of texts to process at once
            device: Device to run the model on ('cuda', 'cpu', or None for auto-detection)
        """
        # Configure logging
        self.logger = logging.getLogger(__name__)
        
        # Set device
        if device is None:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device
            
        self.logger.info(f"Using device: {self.device}")
        
        # Load model and tokenizer
        self.logger.info("Loading FinBERT model and tokenizer...")
        self.tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
        self.model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
        self.model = self.model.to(self.device)
        self.model.eval()  # Set to evaluation mode
        
        self.batch_size = batch_size
        self.labels = ['negative', 'neutral', 'positive']

    def prepare_text(self, text: str) -> str:
        """
        Clean and prepare text for sentiment analysis
        
        Args:
            text: Input text to prepare
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Truncate if too long (FinBERT has a max length of 512 tokens)
        if len(text.split()) > 450:  # Conservative limit
            text = ' '.join(text.split()[:450])
        return text

    def analyze_batch(self, texts: List[str]) -> List[Dict[str, float]]:
        """
        Analyze sentiment for a batch of texts
        
        Args:
            texts: List of texts to analyze
            
        Returns:
            List of dictionaries containing sentiment scores
        """
        prepared_texts = [self.prepare_text(text) for text in texts]
        
        # Tokenize
        encoded = self.tokenizer(
            prepared_texts,
            padding=True,
            truncation=True,
            max_length=512,
            return_tensors='pt'
        )
        
        # Move to device
        input_ids = encoded['input_ids'].to(self.device)
        attention_mask = encoded['attention_mask'].to(self.device)
        
        # Get predictions
        with torch.no_grad():
            outputs = self.model(input_ids, attention_mask=attention_mask)
            probabilities = torch.nn.functional.softmax(outputs.logits, dim=1)
        
        # Convert to numpy for easier handling
        probs_np = probabilities.cpu().numpy()
        
        # Create results
        results = []
        for probs in probs_np:
            sentiment_scores = {
                'negative': float(probs[0]),
                'neutral': float(probs[1]),
                'positive': float(probs[2]),
                'sentiment': self.labels[np.argmax(probs)],
                'confidence': float(np.max(probs))
            }
            results.append(sentiment_scores)
        
        return results

    def analyze_texts(self, texts: List[str], show_progress: bool = True) -> List[Dict[str, float]]:
        """
        Analyze sentiment for a list of texts in batches
        
        Args:
            texts: List of texts to analyze
            show_progress: Whether to show progress bar
            
        Returns:
            List of dictionaries containing sentiment scores
        """
        all_results = []
        
        # Process in batches
        for i in tqdm(range(0, len(texts), self.batch_size), disable=not show_progress):
            batch_texts = texts[i:i + self.batch_size]
            batch_results = self.analyze_batch(batch_texts)
            all_results.extend(batch_results)
        
        return all_results

    def analyze_dataframe(self, 
                         df: pd.DataFrame,
                         text_columns: List[str] = None,
                         show_progress: bool = True) -> pd.DataFrame:
        """
        Analyze sentiment for texts in a DataFrame
        
        Args:
            df: Input DataFrame
            text_columns: List of column names containing text to analyze. 
                         If None, uses 'title' and 'summary' if available
            show_progress: Whether to show progress bar
            
        Returns:
            DataFrame with added sentiment columns
        """
        # Create copy to avoid modifying original
        result_df = df.copy()
        
        # Determine text columns
        if text_columns is None:
            text_columns = []
            if 'title' in df.columns:
                text_columns.append('title')
            if 'summary' in df.columns:
                text_columns.append('summary')
                
        if not text_columns:
            return result_df
            
            
            raise ValueError("No text columns found or specified")
        
        # Combine texts for analysis
        combined_texts = []
        for _, row in df.iterrows():
            text_parts = []
            for col in text_columns:
                if pd.notna(row[col]):
                    text_parts.append(str(row[col]))
            combined_texts.append(' '.join(text_parts))
        
        # Get sentiment scores
        sentiments = self.analyze_texts(combined_texts, show_progress)
        
        # Add results to DataFrame
        result_df['sentiment'] = [s['sentiment'] for s in sentiments]
        result_df['sentiment_confidence'] = [s['confidence'] for s in sentiments]
        result_df['sentiment_negative'] = [s['negative'] for s in sentiments]
        result_df['sentiment_neutral'] = [s['neutral'] for s in sentiments]
        result_df['sentiment_positive'] = [s['positive'] for s in sentiments]
        
        return result_df

    def get_sentiment_summary(self, df: pd.DataFrame) -> Dict:
        """
        Get summary statistics of sentiment analysis results
        
        Args:
            df: DataFrame with sentiment analysis results
            
        Returns:
            Dictionary containing summary statistics
        """
        if 'sentiment' not in df.columns:
            raise ValueError("DataFrame does not contain sentiment analysis results")
            
        summary = {
            'total_articles': len(df),
            'sentiment_distribution': df['sentiment'].value_counts().to_dict(),
            'sentiment_percentages': (df['sentiment'].value_counts(normalize=True) * 100).to_dict(),
            'average_confidence': df['sentiment_confidence'].mean(),
            'average_scores': {
                'negative': df['sentiment_negative'].mean(),
                'neutral': df['sentiment_neutral'].mean(),
                'positive': df['sentiment_positive'].mean()
            }
        }
        return summary