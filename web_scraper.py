import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, quote
from fake_useragent import UserAgent
import re
import time
import json
from typing import Optional, Dict, List, Tuple
import hashlib

class WebScraper:
    def __init__(self):
        self.ua = UserAgent()
        self.session = requests.Session()
        
        # Advanced headers rotation
        self.header_templates = [
            {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0',
            },
            {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-GB,en;q=0.9,en-US;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'DNT': '1',
            }
        ]
        
        # Content extraction cache
        self.extraction_cache = {}
    
    def is_valid_url(self, url: str) -> bool:
        """Enhanced URL validation"""
        try:
            result = urlparse(url)
            # Check for valid scheme and netloc
            if not all([result.scheme in ['http', 'https'], result.netloc]):
                return False
            
            # Check for suspicious patterns
            suspicious_patterns = [
                r'[^\x00-\x7F]',  # Non-ASCII characters
                r'javascript:',    # JavaScript protocol
                r'data:',         # Data URLs
                r'file:',         # File URLs
            ]
            
            for pattern in suspicious_patterns:
                if re.search(pattern, url, re.IGNORECASE):
                    return False
            
            return True
        except:
            return False
    
    def get_random_headers(self) -> Dict[str, str]:
        """Get randomized headers to avoid detection"""
        import random
        
        headers = random.choice(self.header_templates).copy()
        headers['User-Agent'] = self.ua.random
        
        # Add random delays between requests
        time.sleep(random.uniform(0.5, 2.0))
        
        return headers
    
    def detect_content_language(self, soup: BeautifulSoup) -> str:
        """Detect content language"""
        # Check HTML lang attribute
        html_tag = soup.find('html')
        if html_tag and html_tag.get('lang'):
            return html_tag['lang'][:2]
        
        # Check meta tags
        lang_meta = soup.find('meta', attrs={'http-equiv': 'content-language'})
        if lang_meta and lang_meta.get('content'):
            return lang_meta['content'][:2]
        
        # Check meta property
        lang_prop = soup.find('meta', attrs={'property': 'og:locale'})
        if lang_prop and lang_prop.get('content'):
            return lang_prop['content'][:2]
        
        return 'en'  # Default to English
    
    def extract_structured_data(self, soup: BeautifulSoup) -> Dict:
        """Extract structured data (JSON-LD, microdata, etc.)"""
        structured_data = {}
        
        # JSON-LD extraction
        json_scripts = soup.find_all('script', type='application/ld+json')
        for script in json_scripts:
            try:
                data = json.loads(script.string)
                if isinstance(data, dict):
                    structured_data.update(data)
                elif isinstance(data, list) and len(data) > 0:
                    structured_data.update(data[0])
            except:
                continue
        
        # Microdata extraction
        microdata_items = soup.find_all(attrs={'itemtype': True})
        for item in microdata_items:
            item_type = item.get('itemtype', '')
            if 'Article' in item_type:
                properties = item.find_all(attrs={'itemprop': True})
                for prop in properties:
                    prop_name = prop.get('itemprop')
                    prop_value = prop.get_text().strip()
                    if prop_name and prop_value:
                        structured_data[prop_name] = prop_value
        
        return structured_data
    
    def advanced_content_extraction(self, soup: BeautifulSoup) -> Tuple[str, Dict]:
        """Advanced content extraction using multiple strategies"""
        extraction_strategies = [
            self._extract_semantic_content,
            self._extract_by_length_heuristics,
            self._extract_by_text_density,
            self._extract_readability_content
        ]
        
        best_content = ""
        best_score = 0
        best_metadata = {}
        
        for strategy in extraction_strategies:
            try:
                content, metadata, score = strategy(soup)
                if score > best_score and len(content) > 200:
                    best_content = content
                    best_score = score
                    best_metadata = metadata
            except Exception as e:
                continue
        
        return best_content, best_metadata
    
    def _extract_semantic_content(self, soup: BeautifulSoup) -> Tuple[str, Dict, int]:
        """Extract content using semantic HTML elements"""
        selectors = [
            ('article', 100),
            ('main article', 95),
            ('[role="main"] article', 90),
            ('div.article-content', 85),
            ('div.post-content', 85),
            ('div.entry-content', 80),
            ('[itemprop="articleBody"]', 95),
            ('main', 70),
            ('[role="main"]', 65)
        ]
        
        best_element = None
        best_score = 0
        
        for selector, base_score in selectors:
            elements = soup.select(selector)
            for element in elements:
                content_score = self._score_content_quality(element)
                total_score = base_score + content_score
                
                if total_score > best_score:
                    best_score = total_score
                    best_element = element
        
        if best_element:
            content = self.enhanced_text_cleaning(best_element.get_text())
            metadata = self.extract_element_metadata(best_element)
            return content, metadata, best_score
        
        return "", {}, 0
    
    def _extract_by_length_heuristics(self, soup: BeautifulSoup) -> Tuple[str, Dict, int]:
        """Extract content based on text length heuristics"""
        candidates = soup.find_all(['div', 'section', 'article', 'main'])
        
        best_element = None
        best_score = 0
        
        for element in candidates:
            # Remove unwanted child elements
            for unwanted in element.find_all(['nav', 'aside', 'footer', 'header']):
                unwanted.decompose()
            
            text = element.get_text()
            
            # Length-based scoring
            length_score = min(len(text) / 100, 50)  # Max 50 points for length
            
            # Paragraph density
            paragraphs = element.find_all('p')
            para_score = min(len(paragraphs) * 2, 30)  # Max 30 points for paragraphs
            
            # Link ratio (lower is better for content)
            links = element.find_all('a')
            link_text = sum(len(link.get_text()) for link in links)
            link_ratio = link_text / len(text) if len(text) > 0 else 1
            link_penalty = link_ratio * 20  # Penalty for too many links
            
            total_score = length_score + para_score - link_penalty
            
            if total_score > best_score:
                best_score = total_score
                best_element = element
        
        if best_element:
            content = self.enhanced_text_cleaning(best_element.get_text())
            metadata = self.extract_element_metadata(best_element)
            return content, metadata, best_score
        
        return "", {}, 0
    
    def _extract_by_text_density(self, soup: BeautifulSoup) -> Tuple[str, Dict, int]:
        """Extract content based on text density analysis"""
        candidates = soup.find_all(['div', 'section', 'article'])
        
        best_element = None
        best_density = 0
        
        for element in candidates:
            # Calculate text density (text length vs HTML length)
            text_length = len(element.get_text())
            html_length = len(str(element))
            
            if html_length == 0:
                continue
                
            density = text_length / html_length
            
            # Bonus for semantic elements
            if element.name in ['article', 'section']:
                density *= 1.2
            
            # Bonus for content-related classes
            element_classes = ' '.join(element.get('class', []))
            if any(term in element_classes.lower() for term in ['content', 'article', 'post', 'story']):
                density *= 1.1
            
            if density > best_density and text_length > 200:
                best_density = density
                best_element = element
        
        if best_element:
            content = self.enhanced_text_cleaning(best_element.get_text())
            metadata = self.extract_element_metadata(best_element)
            score = int(best_density * 100)
            return content, metadata, score
        
        return "", {}, 0
    
    def _extract_readability_content(self, soup: BeautifulSoup) -> Tuple[str, Dict, int]:
        """Extract content optimized for readability"""
        # Find elements with good readability indicators
        candidates = soup.find_all(['div', 'section', 'article', 'main'])
        
        best_element = None
        best_readability = 0
        
        for element in candidates:
            text = element.get_text()
            
            if len(text) < 100:
                continue
            
            # Readability scoring
            sentences = text.count('.') + text.count('!') + text.count('?')
            words = len(text.split())
            
            if sentences == 0 or words == 0:
                continue
            
            # Average sentence length (ideal range: 15-20 words)
            avg_sentence_length = words / sentences
            sentence_score = max(0, 20 - abs(avg_sentence_length - 17.5))
            
            # Paragraph structure
            paragraphs = element.find_all('p')
            para_score = min(len(paragraphs), 20)
            
            # Headers for structure
            headers = element.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            header_score = min(len(headers) * 3, 15)
            
            total_readability = sentence_score + para_score + header_score
            
            if total_readability > best_readability:
                best_readability = total_readability
                best_element = element
        
        if best_element:
            content = self.enhanced_text_cleaning(best_element.get_text())
            metadata = self.extract_element_metadata(best_element)
            return content, metadata, int(best_readability)
        
        return "", {}, 0
    
    def _score_content_quality(self, element) -> int:
        """Score element based on content quality indicators"""
        if not element:
            return 0
        
        score = 0
        text = element.get_text()
        
        # Length scoring
        text_length = len(text)
        if text_length > 2000:
            score += 30
        elif text_length > 1000:
            score += 20
        elif text_length > 500:
            score += 10
        
        # Paragraph count
        paragraphs = element.find_all('p')
        score += min(len(paragraphs) * 2, 20)
        
        # Header structure
        headers = element.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        score += min(len(headers), 10)
        
        # Class/ID indicators
        element_attrs = f"{element.get('class', [])} {element.get('id', '')}"
        positive_indicators = ['content', 'article', 'post', 'story', 'main', 'body']
        negative_indicators = ['nav', 'menu', 'sidebar', 'footer', 'header', 'ad', 'comment']
        
        for indicator in positive_indicators:
            if indicator in element_attrs.lower():
                score += 5
        
        for indicator in negative_indicators:
            if indicator in element_attrs.lower():
                score -= 10
        
        return max(score, 0)
    
    def enhanced_text_cleaning(self, text: str) -> str:
        """Enhanced text cleaning with better structure preservation"""
        if not text:
            return ""
        
        # Normalize whitespace while preserving structure
        text = re.sub(r'\r\n|\r', '\n', text)  # Normalize line endings
        text = re.sub(r'\t', ' ', text)        # Convert tabs to spaces
        text = re.sub(r'[ ]{2,}', ' ', text)   # Multiple spaces to single
        
        # Clean up line breaks
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Multiple newlines to double
        text = re.sub(r' *\n *', '\n', text)            # Remove spaces around newlines
        
        # Remove excessive punctuation
        text = re.sub(r'[!]{3,}', '!!!', text)
        text = re.sub(r'[?]{3,}', '???', text)
        text = re.sub(r'[.]{4,}', '...', text)
        
        # Remove very short lines (likely navigation)
        lines = text.split('\n')
        cleaned_lines = []
        for line in lines:
            line = line.strip()
            # Keep lines that are either empty (for spacing) or substantial
            if len(line) == 0 or len(line) > 5:
                cleaned_lines.append(line)
        
        # Remove excessive empty lines
        result_lines = []
        empty_count = 0
        for line in cleaned_lines:
            if len(line) == 0:
                empty_count += 1
                if empty_count <= 1:  # Allow max 1 consecutive empty line
                    result_lines.append(line)
            else:
                empty_count = 0
                result_lines.append(line)
        
        return '\n'.join(result_lines).strip()
    
    def extract_element_metadata(self, element) -> Dict:
        """Extract metadata from a specific element"""
        metadata = {}
        
        # Element type and attributes
        metadata['element_type'] = element.name
        metadata['element_id'] = element.get('id', '')
        metadata['element_classes'] = ' '.join(element.get('class', []))
        
        # Content statistics
        text = element.get_text()
        metadata['text_length'] = len(text)
        metadata['word_count'] = len(text.split())
        metadata['paragraph_count'] = len(element.find_all('p'))
        metadata['header_count'] = len(element.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']))
        metadata['link_count'] = len(element.find_all('a'))
        
        return metadata
    
    def extract_comprehensive_metadata(self, soup: BeautifulSoup) -> Dict:
        """Extract comprehensive page metadata"""
        metadata = {}
        
        # Basic metadata
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.get_text().strip()
        
        # Meta tags
        meta_tags = {
            'description': soup.find('meta', attrs={'name': 'description'}),
            'keywords': soup.find('meta', attrs={'name': 'keywords'}),
            'author': soup.find('meta', attrs={'name': 'author'}),
            'publish_date': soup.find('meta', attrs={'property': 'article:published_time'}),
            'modified_date': soup.find('meta', attrs={'property': 'article:modified_time'}),
        }
        
        for key, tag in meta_tags.items():
            if tag and tag.get('content'):
                metadata[key] = tag['content'].strip()
        
        # Open Graph metadata
        og_tags = soup.find_all('meta', attrs={'property': lambda x: x and x.startswith('og:')})
        for tag in og_tags:
            prop = tag.get('property', '').replace('og:', '')
            content = tag.get('content', '').strip()
            if prop and content:
                metadata[f'og_{prop}'] = content
        
        # Twitter Card metadata
        twitter_tags = soup.find_all('meta', attrs={'name': lambda x: x and x.startswith('twitter:')})
        for tag in twitter_tags:
            name = tag.get('name', '').replace('twitter:', '')
            content = tag.get('content', '').strip()
            if name and content:
                metadata[f'twitter_{name}'] = content
        
        # Language
        metadata['language'] = self.detect_content_language(soup)
        
        # Structured data
        structured_data = self.extract_structured_data(soup)
        if structured_data:
            metadata['structured_data'] = structured_data
        
        return metadata
    
    def scrape_article(self, url: str) -> str:
        """Enhanced article scraping with multiple extraction strategies"""
        if not self.is_valid_url(url):
            return "❌ Invalid URL format. Please enter a valid URL starting with http:// or https://"
        
        # Check cache
        url_hash = hashlib.md5(url.encode()).hexdigest()
        if url_hash in self.extraction_cache:
            cached_time, cached_content = self.extraction_cache[url_hash]
            if time.time() - cached_time < 3600:  # 1 hour cache
                return f"📋 [Cached] {cached_content}"
        
        try:
            headers = self.get_random_headers()
            
            # Fetch page with retries
            max_retries = 3
            response = None
            
            for attempt in range(max_retries):
                try:
                    response = self.session.get(url, headers=headers, timeout=20)
                    response.raise_for_status()
                    break
                except requests.exceptions.RequestException as e:
                    if attempt == max_retries - 1:
                        raise e
                    time.sleep(2 ** attempt)  # Exponential backoff
            
            # Validate content type
            content_type = response.headers.get('content-type', '').lower()
            if 'text/html' not in content_type:
                return f"❌ Invalid content type: {content_type}. This appears to be a {content_type.split('/')[0]} file, not a webpage."
            
            # Parse HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove unwanted elements
            unwanted_selectors = [
                'script', 'style', 'nav', 'header', 'footer', 'aside', 
                '.advertisement', '.ad', '.sidebar', '.comments', 
                '.social-share', '.related-articles', '#comments'
            ]
            
            for selector in unwanted_selectors:
                for element in soup.select(selector):
                    element.decompose()
            
            # Extract comprehensive metadata
            metadata = self.extract_comprehensive_metadata(soup)
            
            # Advanced content extraction
            content, content_metadata = self.advanced_content_extraction(soup)
            
            # Validate content quality
            if len(content) < 150:
                return "❌ Could not extract significant content. This page might use dynamic loading, be behind a paywall, or contain primarily multimedia content."
            
            # Format final output
            result_parts = []
            
            # Add metadata header
            if metadata.get('title'):
                result_parts.append(f"📰 **{metadata['title']}**\n")
            
            if metadata.get('author'):
                result_parts.append(f"✍️ Author: {metadata['author']}")
            
            if metadata.get('publish_date'):
                result_parts.append(f"📅 Published: {metadata['publish_date'][:10]}")
            
            if metadata.get('description'):
                result_parts.append(f"📝 Description: {metadata['description']}")
            
            if result_parts:
                result_parts.append("─" * 60)
            
            result_parts.append(content)
            
            # Add extraction info
            if content_metadata:
                result_parts.append(f"\n📊 Extracted from {content_metadata.get('element_type', 'unknown')} element")
                result_parts.append(f"📏 Content: {content_metadata.get('word_count', 0)} words, {content_metadata.get('paragraph_count', 0)} paragraphs")
            
            final_content = '\n'.join(result_parts)
            
            # Cache result
            self.extraction_cache[url_hash] = (time.time(), final_content)
            
            # Limit cache size
            if len(self.extraction_cache) > 50:
                oldest_key = min(self.extraction_cache.keys(), 
                               key=lambda k: self.extraction_cache[k][0])
                del self.extraction_cache[oldest_key]
            
            return final_content
            
        except requests.exceptions.Timeout:
            return "⏰ Request timed out. The website is taking too long to respond."
        except requests.exceptions.ConnectionError:
            return "🌐 Connection failed. Please check your internet connection or try again later."
        except requests.exceptions.HTTPError as e:
            status_code = e.response.status_code
            if status_code == 403:
                return "🚫 Access denied. The website is blocking automated requests."
            elif status_code == 404:
                return "🔍 Page not found. Please verify the URL is correct."
            elif status_code == 429:
                return "⏱️ Rate limited. The website is temporarily blocking requests. Try again later."
            elif status_code >= 500:
                return f"🔧 Server error ({status_code}). The website is experiencing technical difficulties."
            else:
                return f"📄 HTTP error {status_code}. The website returned an error response."
        except Exception as e:
            return f"⚠️ Unexpected error: {str(e)}"
    
    def get_site_info(self, url: str) -> Dict[str, str]:
        """Get detailed information about a website"""
        if not self.is_valid_url(url):
            return {"error": "Invalid URL format"}
        
        try:
            headers = self.get_random_headers()
            response = self.session.head(url, headers=headers, timeout=10, allow_redirects=True)
            
            info = {
                "status_code": response.status_code,
                "final_url": response.url,
                "content_type": response.headers.get('content-type', 'unknown'),
                "content_length": response.headers.get('content-length', 'unknown'),
                "server": response.headers.get('server', 'unknown'),
                "last_modified": response.headers.get('last-modified', 'unknown'),
                "cache_control": response.headers.get('cache-control', 'unknown')
            }
            
            # Check if URL was redirected
            if response.url != url:
                info["redirected"] = True
                info["redirect_count"] = len(response.history)
            
            return info
            
        except Exception as e:
            return {"error": str(e)}
    
    def clear_cache(self):
        """Clear the extraction cache"""
        self.extraction_cache.clear()