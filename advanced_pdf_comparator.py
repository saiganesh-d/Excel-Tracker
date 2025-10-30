"""
Advanced PDF Comparator - Main orchestration engine

This module integrates all comparison components into a unified workflow:
- Paragraph extraction
- Language detection
- Translation (if needed)
- Semantic comparison
- Requirement analysis
- LLM explanations (optional)

Provides complete end-to-end PDF comparison with high accuracy.

Author: Advanced PDF Comparison System
Date: 2025-10-30
"""

import json
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    print("[!] pdfplumber not available. Run: pip install pdfplumber")

# Import our components
from paragraph_extractor import ParagraphExtractor
from language_detector import LanguageDetector
from translation_service import LocalTranslator
from semantic_embedder import SemanticEmbedder
from semantic_comparator import SemanticComparator
from requirement_analyzer import RequirementAnalyzer
from local_llm import LocalLLM, ExplanationGenerator


@dataclass
class ComparisonConfig:
    """
    Configuration for PDF comparison

    Attributes:
        enable_translation: Enable automatic translation
        enable_requirements: Enable requirement analysis
        enable_llm: Enable LLM explanations
        similarity_threshold: Minimum similarity for matching (0-1)
        use_gpu: Use GPU acceleration
        llm_model_path: Path to LLM model (if enable_llm=True)
        max_llm_explanations: Maximum LLM explanations to generate
    """
    enable_translation: bool = True
    enable_requirements: bool = True
    enable_llm: bool = False
    similarity_threshold: float = 0.75
    use_gpu: bool = True
    llm_model_path: Optional[str] = None
    max_llm_explanations: int = 10


@dataclass
class DocumentInfo:
    """Information about a document"""
    file_path: str
    language: str
    paragraph_count: int
    character_count: int
    requirement_count: int = 0
    needs_translation: bool = False


@dataclass
class ComparisonReport:
    """
    Complete comparison report

    Contains all comparison results and metadata
    """
    old_doc_info: DocumentInfo
    new_doc_info: DocumentInfo
    comparison_result: Dict
    requirement_changes: List[Dict] = field(default_factory=list)
    llm_explanations: List[Dict] = field(default_factory=list)
    config: ComparisonConfig = None
    timestamp: str = None
    processing_time: float = 0.0

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'timestamp': self.timestamp,
            'processing_time': round(self.processing_time, 2),
            'old_document': {
                'file_path': self.old_doc_info.file_path,
                'language': self.old_doc_info.language,
                'paragraphs': self.old_doc_info.paragraph_count,
                'characters': self.old_doc_info.character_count,
                'requirements': self.old_doc_info.requirement_count,
                'translated': self.old_doc_info.needs_translation
            },
            'new_document': {
                'file_path': self.new_doc_info.file_path,
                'language': self.new_doc_info.language,
                'paragraphs': self.new_doc_info.paragraph_count,
                'characters': self.new_doc_info.character_count,
                'requirements': self.new_doc_info.requirement_count,
                'translated': self.new_doc_info.needs_translation
            },
            'comparison': self.comparison_result,
            'requirement_changes': self.requirement_changes,
            'llm_explanations': self.llm_explanations,
            'config': {
                'translation': self.config.enable_translation,
                'requirements': self.config.enable_requirements,
                'llm': self.config.enable_llm,
                'similarity_threshold': self.config.similarity_threshold
            } if self.config else {}
        }

    def save_json(self, output_path: str):
        """Save report to JSON file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)
        print(f"[+] Report saved to: {output_path}")


class AdvancedPDFComparator:
    """
    Advanced PDF comparison engine

    Orchestrates all comparison components to provide comprehensive
    document comparison with semantic understanding, requirement tracking,
    and optional LLM explanations.
    """

    def __init__(self, config: Optional[ComparisonConfig] = None):
        """
        Initialize comparator

        Args:
            config: Comparison configuration
        """
        self.config = config or ComparisonConfig()

        print("=" * 60)
        print("ADVANCED PDF COMPARATOR")
        print("=" * 60)

        # Initialize components
        print("\n[i] Initializing components...")

        self.paragraph_extractor = ParagraphExtractor()
        print("[+] Paragraph extractor ready")

        self.language_detector = LanguageDetector()
        print("[+] Language detector ready")

        if self.config.enable_translation:
            self.translator = LocalTranslator()
            print("[+] Translator ready")

        self.embedder = SemanticEmbedder(use_gpu=self.config.use_gpu)
        print("[+] Semantic embedder ready")

        self.comparator = SemanticComparator(
            embedder=self.embedder,
            similarity_threshold=self.config.similarity_threshold
        )
        print("[+] Semantic comparator ready")

        if self.config.enable_requirements:
            self.requirement_analyzer = RequirementAnalyzer()
            print("[+] Requirement analyzer ready")

        if self.config.enable_llm:
            self.llm = LocalLLM(
                model_path=self.config.llm_model_path,
                use_gpu=self.config.use_gpu
            )
            self.explanation_generator = ExplanationGenerator(self.llm)
            print("[+] LLM explanation generator ready")

        print("\n[+] All components initialized")
        print("=" * 60)

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from PDF file

        Args:
            pdf_path: Path to PDF file

        Returns:
            Extracted text
        """
        if not PDFPLUMBER_AVAILABLE:
            print("[!] pdfplumber not available, cannot extract PDF")
            return ""

        try:
            text_content = []

            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        text_content.append(text)

            return "\n\n".join(text_content)

        except Exception as e:
            print(f"[-] Error extracting PDF: {e}")
            return ""

    def analyze_document(
        self,
        pdf_path: str,
        extract_requirements: bool = True
    ) -> Tuple[List[str], DocumentInfo]:
        """
        Analyze a single document

        Args:
            pdf_path: Path to PDF file
            extract_requirements: Whether to extract requirements

        Returns:
            (paragraphs, document_info)
        """
        print(f"\n[i] Analyzing: {Path(pdf_path).name}")

        # Extract text
        print("[i] Extracting text...")
        text = self.extract_text_from_pdf(pdf_path)

        if not text:
            print("[-] No text extracted")
            return [], DocumentInfo(
                file_path=pdf_path,
                language='unknown',
                paragraph_count=0,
                character_count=0
            )

        # Extract paragraphs
        print("[i] Extracting paragraphs...")
        paragraphs = self.paragraph_extractor.extract_paragraphs(text)
        print(f"[+] Extracted {len(paragraphs)} paragraphs")

        # Detect language
        print("[i] Detecting language...")
        lang_result = self.language_detector.detect_document_language(paragraphs)
        print(f"[+] Language: {lang_result.language_name} ({lang_result.confidence:.0%} confidence)")

        # Analyze requirements if enabled
        requirement_count = 0
        if extract_requirements and self.config.enable_requirements:
            print("[i] Analyzing requirements...")
            requirements = self.requirement_analyzer.analyze_paragraphs(paragraphs)
            requirement_count = len(requirements)
            print(f"[+] Found {requirement_count} requirements")

        # Check if translation needed
        needs_translation = (
            self.config.enable_translation and
            lang_result.language not in ['en', 'unknown']
        )

        doc_info = DocumentInfo(
            file_path=pdf_path,
            language=lang_result.language_name,
            paragraph_count=len(paragraphs),
            character_count=len(text),
            requirement_count=requirement_count,
            needs_translation=needs_translation
        )

        return paragraphs, doc_info

    def translate_if_needed(
        self,
        paragraphs: List[str],
        source_language: str
    ) -> List[str]:
        """
        Translate paragraphs if needed

        Args:
            paragraphs: List of paragraphs
            source_language: Source language code

        Returns:
            Translated paragraphs (or original if no translation needed)
        """
        if not self.config.enable_translation:
            return paragraphs

        if source_language == 'en':
            return paragraphs

        # Translate to English
        print(f"\n[i] Translating from {source_language} to English...")
        translated = self.translator.translate_batch(
            paragraphs,
            source_lang=source_language,
            target_lang='en'
        )
        print(f"[+] Translated {len(translated)} paragraphs")

        return translated

    def compare_documents(
        self,
        old_pdf_path: str,
        new_pdf_path: str
    ) -> ComparisonReport:
        """
        Compare two PDF documents

        Args:
            old_pdf_path: Path to old/original PDF
            new_pdf_path: Path to new/modified PDF

        Returns:
            ComparisonReport with complete results
        """
        import time
        start_time = time.time()

        print("\n" + "=" * 60)
        print("STARTING DOCUMENT COMPARISON")
        print("=" * 60)

        # Analyze both documents
        print("\n[STEP 1] Analyzing documents...")
        old_paragraphs, old_doc_info = self.analyze_document(old_pdf_path)
        new_paragraphs, new_doc_info = self.analyze_document(new_pdf_path)

        if not old_paragraphs or not new_paragraphs:
            print("[-] Cannot compare - no content extracted")
            return None

        # Translate if needed
        print("\n[STEP 2] Translation check...")
        old_lang_code = self.language_detector.get_language_code(old_doc_info.language)
        new_lang_code = self.language_detector.get_language_code(new_doc_info.language)

        old_paragraphs_translated = self.translate_if_needed(old_paragraphs, old_lang_code)
        new_paragraphs_translated = self.translate_if_needed(new_paragraphs, new_lang_code)

        # Semantic comparison
        print("\n[STEP 3] Semantic comparison...")
        comparison_result = self.comparator.compare_paragraphs(
            old_paragraphs_translated,
            new_paragraphs_translated
        )

        # Requirement analysis
        requirement_changes = []
        if self.config.enable_requirements:
            print("\n[STEP 4] Requirement analysis...")
            old_requirements = self.requirement_analyzer.analyze_paragraphs(old_paragraphs_translated)
            new_requirements = self.requirement_analyzer.analyze_paragraphs(new_paragraphs_translated)

            requirement_changes_obj = self.requirement_analyzer.compare_requirements(
                old_requirements,
                new_requirements
            )

            requirement_changes = [rc.to_dict() for rc in requirement_changes_obj]
            print(f"[+] Analyzed {len(requirement_changes)} requirement changes")

        # LLM explanations
        llm_explanations = []
        if self.config.enable_llm:
            print("\n[STEP 5] Generating LLM explanations...")
            matches_with_explanations = self.explanation_generator.explain_matches(
                [m.to_dict() for m in comparison_result.matches[:self.config.max_llm_explanations]]
            )

            llm_explanations = [
                {
                    'match_index': i,
                    'explanation': m.get('llm_explanation', '')
                }
                for i, m in enumerate(matches_with_explanations)
                if 'llm_explanation' in m
            ]
            print(f"[+] Generated {len(llm_explanations)} explanations")

        # Build report
        end_time = time.time()
        processing_time = end_time - start_time

        report = ComparisonReport(
            old_doc_info=old_doc_info,
            new_doc_info=new_doc_info,
            comparison_result=comparison_result.to_dict(),
            requirement_changes=requirement_changes,
            llm_explanations=llm_explanations,
            config=self.config,
            processing_time=processing_time
        )

        print("\n" + "=" * 60)
        print("COMPARISON COMPLETE")
        print("=" * 60)
        print(f"Processing time: {processing_time:.2f} seconds")
        print(f"\nSummary:")
        print(f"  Unchanged: {comparison_result.unchanged_count}")
        print(f"  Modified: {comparison_result.modified_count}")
        print(f"  Added: {comparison_result.added_count}")
        print(f"  Deleted: {comparison_result.deleted_count}")
        print(f"  Moved: {comparison_result.moved_count}")
        print(f"  Average similarity: {comparison_result.average_similarity:.2%}")

        if requirement_changes:
            critical_req_changes = sum(
                1 for rc in requirement_changes
                if rc.get('severity') == 'critical'
            )
            print(f"\nRequirement Changes:")
            print(f"  Total: {len(requirement_changes)}")
            print(f"  Critical: {critical_req_changes}")

        print("=" * 60)

        return report

    def compare_texts(
        self,
        old_text: str,
        new_text: str
    ) -> ComparisonReport:
        """
        Compare two text strings directly (without PDF extraction)

        Args:
            old_text: Original text
            new_text: Modified text

        Returns:
            ComparisonReport
        """
        import time
        start_time = time.time()

        print("\n[i] Comparing text strings...")

        # Extract paragraphs
        old_paragraphs = self.paragraph_extractor.extract_paragraphs(old_text)
        new_paragraphs = self.paragraph_extractor.extract_paragraphs(new_text)

        # Detect languages
        old_lang = self.language_detector.detect_document_language(old_paragraphs)
        new_lang = self.language_detector.detect_document_language(new_paragraphs)

        # Create document info
        old_doc_info = DocumentInfo(
            file_path="text_input",
            language=old_lang.language_name,
            paragraph_count=len(old_paragraphs),
            character_count=len(old_text)
        )

        new_doc_info = DocumentInfo(
            file_path="text_input",
            language=new_lang.language_name,
            paragraph_count=len(new_paragraphs),
            character_count=len(new_text)
        )

        # Semantic comparison
        comparison_result = self.comparator.compare_paragraphs(
            old_paragraphs,
            new_paragraphs
        )

        # Requirement analysis
        requirement_changes = []
        if self.config.enable_requirements:
            old_requirements = self.requirement_analyzer.analyze_paragraphs(old_paragraphs)
            new_requirements = self.requirement_analyzer.analyze_paragraphs(new_paragraphs)

            requirement_changes_obj = self.requirement_analyzer.compare_requirements(
                old_requirements,
                new_requirements
            )
            requirement_changes = [rc.to_dict() for rc in requirement_changes_obj]

        end_time = time.time()

        report = ComparisonReport(
            old_doc_info=old_doc_info,
            new_doc_info=new_doc_info,
            comparison_result=comparison_result.to_dict(),
            requirement_changes=requirement_changes,
            config=self.config,
            processing_time=end_time - start_time
        )

        return report


def main():
    """Example usage"""
    print("Advanced PDF Comparator - Example Usage\n")

    # Configure comparison
    config = ComparisonConfig(
        enable_translation=True,
        enable_requirements=True,
        enable_llm=False,  # Disabled for demo (no model)
        similarity_threshold=0.75,
        use_gpu=True
    )

    # Initialize comparator
    comparator = AdvancedPDFComparator(config)

    # Example: Compare text strings
    print("\n[EXAMPLE] Comparing text strings...")

    old_text = """
    The system must authenticate all users.
    User passwords shall be encrypted using AES-256.
    The interface should be user-friendly.
    Response time must be under 2 seconds.
    """

    new_text = """
    The system must verify user credentials.
    All passwords shall be encrypted using AES-256 standard.
    The interface must be intuitive and accessible.
    Response time should be under 2 seconds for normal operations.
    The system must log all authentication attempts.
    """

    report = comparator.compare_texts(old_text, new_text)

    if report:
        print("\n[+] Comparison successful!")
        print(f"[i] Processing time: {report.processing_time:.2f}s")

        # Save report
        # report.save_json('comparison_report.json')

    print("\n" + "=" * 60)
    print("For PDF comparison, use:")
    print("  report = comparator.compare_documents('old.pdf', 'new.pdf')")
    print("=" * 60)


if __name__ == "__main__":
    main()
