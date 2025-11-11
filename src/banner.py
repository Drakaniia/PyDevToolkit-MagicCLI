"""
Banner utilities for displaying stylized text
"""
from pyfiglet import Figlet

def create_qwenzyy_banner(font_style="doom"):
    """
    Create QWENZYY banner using pyfiglet
    
    Args:
        font_style: Font style to use (doom, block, lean, etc.)
    
    Returns:
        str: The rendered banner text
    """
    try:
        fig = Figlet(font=font_style)
        return fig.renderText("QWENZYY")
    except Exception:
        # Fallback to manual ASCII if pyfiglet fails
        return get_manual_qwenzyy_banner()

def get_manual_qwenzyy_banner():
    """
    Manual ASCII art banner as fallback with shadow effect
    Light source from north-east, shadow on south-west
    """
    return """
    
 ███           ██████      █████   ███   █████
░░░██        ███░░░░███   ░░███   ░███  ░░███ 
  ░░██      ███    ░░███   ░███   ░███   ░███ 
   ░░███   ░███     ░███   ░███   ░███   ░███ 
    ██░    ░███     ░███   ░░███  █████  ███  
   ██      ░░███ ░░████     ░░░█████░█████░   
 ███        ░░░██████░██      ░░███ ░░███     
░░░          ░░░░░░ ░░         ░░░   ░░░                           
"""

def get_available_fonts():
    """
    Get list of available fonts that work well for banners
    """
    return ["doom", "block", "lean", "big", "slant", "standard"]