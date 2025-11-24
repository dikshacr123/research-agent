import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

# File paths for persistent storage
DATA_DIR = Path("data")
CONVERSATION_FILE = DATA_DIR / "conversation_history.json"
ACCOUNT_PLAN_FILE = DATA_DIR / "account_plan.json"
OUTPUT_FILE = DATA_DIR / "output.json"

# Ensure data directory exists
DATA_DIR.mkdir(exist_ok=True)


def save_json_file(filepath: Path, data: any) -> bool:
    """
    Save data to a JSON file.
    
    Args:
        filepath: Path to the file
        data: Data to save (must be JSON serializable)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error saving to {filepath}: {e}")
        return False


def load_json_file(filepath: Path, default: any = None) -> any:
    """
    Load data from a JSON file.
    
    Args:
        filepath: Path to the file
        default: Default value if file doesn't exist or can't be read
        
    Returns:
        Loaded data or default value
    """
    try:
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return default
    except Exception as e:
        print(f"Error loading from {filepath}: {e}")
        return default


def save_conversation_history(messages: List[Dict]) -> bool:
    """
    Save conversation history to file.
    
    Args:
        messages: List of message dictionaries
        
    Returns:
        True if successful
    """
    return save_json_file(CONVERSATION_FILE, messages)


def load_conversation_history() -> List[Dict]:
    """
    Load conversation history from file.
    
    Returns:
        List of message dictionaries
    """
    return load_json_file(CONVERSATION_FILE, default=[])


def save_account_plan(plan: Optional[Dict[str, str]]) -> bool:
    """
    Save account plan to file.
    
    Args:
        plan: Account plan dictionary or None
        
    Returns:
        True if successful
    """
    if plan is None:
        # If plan is None, save empty dict or delete file
        return save_json_file(ACCOUNT_PLAN_FILE, {})
    
    # Add metadata
    plan_with_metadata = {
        "plan": plan,
        "created_at": datetime.now().isoformat(),
        "version": "1.0"
    }
    
    return save_json_file(ACCOUNT_PLAN_FILE, plan_with_metadata)


def load_account_plan() -> Optional[Dict[str, str]]:
    """
    Load account plan from file.
    
    Returns:
        Account plan dictionary or None
    """
    data = load_json_file(ACCOUNT_PLAN_FILE)
    
    if data and "plan" in data:
        return data["plan"]
    elif data and isinstance(data, dict) and any(k in data for k in [
        'company_overview', 'key_stakeholders', 'pain_points'
    ]):
        # Legacy format without metadata wrapper
        return data
    
    return None


def export_plan_to_json(plan: Dict[str, str], include_timestamp: bool = True) -> str:
    """
    Export account plan to formatted JSON string.
    
    Args:
        plan: Account plan dictionary
        include_timestamp: Whether to include timestamp in export
        
    Returns:
        Formatted JSON string
    """
    export_data = plan.copy()
    
    if include_timestamp:
        export_data["exported_at"] = datetime.now().isoformat()
    
    return json.dumps(export_data, indent=2, ensure_ascii=False)


def save_output(data: Dict, filename: str = "output.json") -> bool:
    """
    Save output data to a specified file.
    
    Args:
        data: Data to save
        filename: Output filename
        
    Returns:
        True if successful
    """
    output_path = DATA_DIR / filename
    
    # Add timestamp to output
    output_data = {
        "data": data,
        "timestamp": datetime.now().isoformat(),
        "type": "account_plan_output"
    }
    
    return save_json_file(output_path, output_data)


def format_plan_display(plan: Dict[str, str]) -> str:
    """
    Format account plan for display in terminal/logs.
    
    Args:
        plan: Account plan dictionary
        
    Returns:
        Formatted string representation
    """
    output = "\n" + "="*80 + "\n"
    output += "ACCOUNT PLAN\n"
    output += "="*80 + "\n\n"
    
    for section_key, section_value in plan.items():
        section_title = section_key.replace('_', ' ').upper()
        output += f"{section_title}\n"
        output += "-" * len(section_title) + "\n"
        output += f"{section_value}\n\n"
    
    output += "="*80 + "\n"
    
    return output


def validate_account_plan(plan: Dict) -> tuple[bool, List[str]]:
    """
    Validate that an account plan has all required sections.
    
    Args:
        plan: Account plan dictionary
        
    Returns:
        Tuple of (is_valid, list_of_missing_sections)
    """
    required_sections = [
        'company_overview',
        'key_stakeholders',
        'pain_points',
        'value_proposition',
        'engagement_strategy',
        'success_metrics',
        'next_steps'
    ]
    
    missing_sections = [
        section for section in required_sections 
        if section not in plan or not plan[section]
    ]
    
    is_valid = len(missing_sections) == 0
    
    return is_valid, missing_sections


def merge_plan_sections(original_plan: Dict, updates: Dict) -> Dict:
    """
    Merge updates into original plan while preserving other sections.
    
    Args:
        original_plan: Original account plan
        updates: Dictionary of section updates
        
    Returns:
        Merged account plan
    """
    merged = original_plan.copy()
    merged.update(updates)
    return merged


def clean_text(text: str) -> str:
    """
    Clean and normalize text content.
    
    Args:
        text: Input text
        
    Returns:
        Cleaned text
    """
    # Remove excessive whitespace
    text = ' '.join(text.split())
    
    # Remove markdown artifacts if any
    text = text.replace('```', '').replace('**', '')
    
    return text.strip()


def truncate_text(text: str, max_length: int = 500, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.
    
    Args:
        text: Input text
        max_length: Maximum length
        suffix: Suffix to add if truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def format_timestamp(iso_string: str = None) -> str:
    """
    Format timestamp for display.
    
    Args:
        iso_string: ISO format timestamp string, or None for current time
        
    Returns:
        Formatted timestamp string
    """
    if iso_string:
        dt = datetime.fromisoformat(iso_string)
    else:
        dt = datetime.now()
    
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def create_backup(filepath: Path) -> bool:
    """
    Create a backup of a file.
    
    Args:
        filepath: Path to file to backup
        
    Returns:
        True if successful
    """
    try:
        if not filepath.exists():
            return False
        
        backup_dir = DATA_DIR / "backups"
        backup_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{filepath.stem}_{timestamp}{filepath.suffix}"
        backup_path = backup_dir / backup_filename
        
        import shutil
        shutil.copy2(filepath, backup_path)
        
        return True
    except Exception as e:
        print(f"Error creating backup: {e}")
        return False


def get_file_age_days(filepath: Path) -> Optional[int]:
    """
    Get the age of a file in days.
    
    Args:
        filepath: Path to file
        
    Returns:
        Age in days, or None if file doesn't exist
    """
    try:
        if not filepath.exists():
            return None
        
        modified_time = datetime.fromtimestamp(filepath.stat().st_mtime)
        age = datetime.now() - modified_time
        
        return age.days
    except Exception as e:
        print(f"Error getting file age: {e}")
        return None


def cleanup_old_backups(days_to_keep: int = 7) -> int:
    """
    Clean up backup files older than specified days.
    
    Args:
        days_to_keep: Number of days to keep backups
        
    Returns:
        Number of files deleted
    """
    backup_dir = DATA_DIR / "backups"
    
    if not backup_dir.exists():
        return 0
    
    deleted_count = 0
    
    try:
        for backup_file in backup_dir.iterdir():
            if backup_file.is_file():
                age = get_file_age_days(backup_file)
                if age and age > days_to_keep:
                    backup_file.unlink()
                    deleted_count += 1
    except Exception as e:
        print(f"Error cleaning up backups: {e}")
    
    return deleted_count


def export_conversation_to_text(messages: List[Dict], filepath: Path = None) -> str:
    """
    Export conversation history to readable text format.
    
    Args:
        messages: List of message dictionaries
        filepath: Optional path to save the text file
        
    Returns:
        Formatted conversation text
    """
    output = []
    output.append("="*80)
    output.append("CONVERSATION HISTORY")
    output.append("="*80)
    output.append("")
    
    for msg in messages:
        role = msg.get('role', 'unknown').upper()
        content = msg.get('content', '')
        timestamp = msg.get('timestamp', '')
        
        if timestamp:
            output.append(f"[{format_timestamp(timestamp)}] {role}:")
        else:
            output.append(f"{role}:")
        
        output.append(content)
        output.append("")
        output.append("-"*80)
        output.append("")
    
    text_output = "\n".join(output)
    
    if filepath:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(text_output)
        except Exception as e:
            print(f"Error saving conversation text: {e}")
    
    return text_output


# Initialize data directory and create sample output.json on first run
def initialize_data_directory():
    """Initialize data directory with sample structure."""
    if not OUTPUT_FILE.exists():
        sample_output = {
            "message": "This file will contain exported account plans",
            "created_at": datetime.now().isoformat(),
            "version": "1.0"
        }
        save_json_file(OUTPUT_FILE, sample_output)


# Run initialization
initialize_data_directory()