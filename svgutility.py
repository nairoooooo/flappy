import pygame
import os
import xml.etree.ElementTree as ET
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPM
from PIL import Image
import io

def add_accessibility_to_svg(svg_path):
    """
    Add accessibility attributes to SVG files if they don't exist.
    Returns the path to the modified SVG or the original if modification fails.
    """
    try:
        # Parse the SVG
        tree = ET.parse(svg_path)
        root = tree.getroot()
        
        # Extract filename without extension to use as title/description
        filename = os.path.basename(svg_path).replace('.svg', '')
        
        # Add title if it doesn't exist
        title_element = root.find('.//{http://www.w3.org/2000/svg}title')
        if title_element is None:
            title_element = ET.Element("{http://www.w3.org/2000/svg}title")
            title_element.text = filename.capitalize()
            root.insert(0, title_element)
            
        # Add description if it doesn't exist
        desc_element = root.find('.//{http://www.w3.org/2000/svg}desc')
        if desc_element is None:
            desc_element = ET.Element("{http://www.w3.org/2000/svg}desc")
            desc_element.text = f"Game element: {filename}"
            if root.find('.//{http://www.w3.org/2000/svg}title') is not None:
                root.insert(1, desc_element)
            else:
                root.insert(0, desc_element)
                
        # Add ARIA role if not present
        if 'role' not in root.attrib:
            root.set('role', 'img')
        
        # Add aria-labelledby if not present
        if 'aria-labelledby' not in root.attrib and title_element is not None:
            if 'id' not in title_element.attrib:
                title_id = f"{filename}_title"
                title_element.set('id', title_id)
            else:
                title_id = title_element.get('id')
                
            if desc_element is not None:
                if 'id' not in desc_element.attrib:
                    desc_id = f"{filename}_desc"
                    desc_element.set('id', desc_id)
                else:
                    desc_id = desc_element.get('id')
                root.set('aria-labelledby', f"{title_id} {desc_id}")
            else:
                root.set('aria-labelledby', title_id)
        
        # Create a temporary modified file
        temp_path = f"{svg_path.replace('.svg', '')}_accessible.svg"
        tree.write(temp_path)
        return temp_path
    except Exception as e:
        print(f"Error adding accessibility to {svg_path}: {e}")
        return svg_path  # Return original file if modification fails

def audit_svg_files(directory="img/"):
    """
    Check all SVG files in the directory for accessibility issues.
    """
    if not os.path.exists(directory):
        print(f"Directory not found: {directory}")
        return []
        
    svg_files = [f for f in os.listdir(directory) if f.endswith('.svg')]
    print(f"Found {len(svg_files)} SVG files to audit")
    
    issues = []
    
    for svg_file in svg_files:
        file_path = os.path.join(directory, svg_file)
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            
            file_issues = []
            
            # Check for title
            if root.find('.//{http://www.w3.org/2000/svg}title') is None:
                file_issues.append("Missing <title> element")
                
            # Check for description
            if root.find('.//{http://www.w3.org/2000/svg}desc') is None:
                file_issues.append("Missing <desc> element")
                
            # Check for role attribute
            if 'role' not in root.attrib:
                file_issues.append("Missing 'role' attribute")
                
            # Check for aria-labelledby
            if 'aria-labelledby' not in root.attrib:
                file_issues.append("Missing 'aria-labelledby' attribute")
            
            # Check SVG validity
            try:
                drawing = svg2rlg(file_path)
                if drawing is None:
                    file_issues.append("SVG cannot be rendered")
            except Exception as e:
                file_issues.append(f"SVG rendering error: {str(e)}")
            
            if file_issues:
                issues.append((svg_file, file_issues))
                
        except Exception as e:
            issues.append((svg_file, [f"Error parsing SVG: {e}"]))
    
    if issues:
        print("\nSVG Accessibility Issues:")
        for file_name, file_issues in issues:
            print(f"\n{file_name}:")
            for issue in file_issues:
                print(f"  - {issue}")
    else:
        print("\nNo SVG accessibility issues found!")
    
    return issues

def batch_process_svgs(directory="img/"):
    """
    Process all SVG files in the directory to add accessibility features.
    Creates backup files before modifying.
    """
    if not os.path.exists(directory):
        print(f"Directory not found: {directory}")
        return 0, 0
        
    svg_files = [f for f in os.listdir(directory) if f.endswith('.svg')]
    print(f"Found {len(svg_files)} SVG files to process")
    
    processed_files = 0
    skipped_files = 0
    
    for svg_file in svg_files:
        file_path = os.path.join(directory, svg_file)
        backup_path = file_path + ".backup"
        
        # Only create a backup if it doesn't exist
        if not os.path.exists(backup_path):
            try:
                # Create backup
                with open(file_path, 'rb') as src_file:
                    with open(backup_path, 'wb') as backup_file:
                        backup_file.write(src_file.read())
                
                # Get accessible version
                accessible_path = add_accessibility_to_svg(file_path)
                
                # If a new file was created, replace the original
                if accessible_path != file_path:
                    with open(accessible_path, 'rb') as acc_file:
                        with open(file_path, 'wb') as orig_file:
                            orig_file.write(acc_file.read())
                    
                    # Remove temporary file
                    try:
                        os.remove(accessible_path)
                    except:
                        pass
                    
                    processed_files += 1
                    print(f"Processed: {svg_file}")
                else:
                    skipped_files += 1
                    print(f"Skipped (no changes needed): {svg_file}")
                    
            except Exception as e:
                print(f"Error processing {svg_file}: {e}")
                skipped_files += 1
        else:
            print(f"Skipped (backup exists): {svg_file}")
            skipped_files += 1
    
    print(f"\nProcessing complete! Processed: {processed_files}, Skipped: {skipped_files}")
    
    # Run an audit to verify the results
    print("\nRunning post-processing audit...")
    audit_svg_files(directory)
    
    return processed_files, skipped_files

def restore_backups(directory="img/"):
    """
    Restore all SVG files from their backups.
    """
    if not os.path.exists(directory):
        print(f"Directory not found: {directory}")
        return 0
        
    backup_files = [f for f in os.listdir(directory) if f.endswith('.svg.backup')]
    print(f"Found {len(backup_files)} backup files to restore")
    
    restored_files = 0
    
    for backup_file in backup_files:
        backup_path = os.path.join(directory, backup_file)
        original_path = backup_path.replace('.backup', '')
        
        try:
            # Restore from backup
            with open(backup_path, 'rb') as src_file:
                with open(original_path, 'wb') as orig_file:
                    orig_file.write(src_file.read())
            
            # Remove backup
            os.remove(backup_path)
            
            restored_files += 1
            print(f"Restored: {original_path}")
                
        except Exception as e:
            print(f"Error restoring {original_path}: {e}")
    
    print(f"\nRestore complete! Restored: {restored_files}")
    return restored_files

def verify_svg(svg_path):
    """
    Verify that an SVG file can be properly loaded and rendered.
    Returns (success, message)
    """
    try:
        # Try parsing as XML
        tree = ET.parse(svg_path)
        root = tree.getroot()
        
        # Try rendering with svglib
        drawing = svg2rlg(svg_path)
        if drawing is None:
            return False, "SVG parsed but cannot be rendered"
            
        # Try converting to PNG in memory
        bio = io.BytesIO()
        renderPM.drawToFile(drawing, bio, fmt="PNG")
        bio.seek(0)
        
        # Try loading as PIL Image
        img = Image.open(bio)
        
        return True, "SVG is valid and can be rendered"
        
    except ET.ParseError as e:
        return False, f"XML parsing error: {str(e)}"
    except Exception as e:
        return False, f"Error: {str(e)}"

if __name__ == "__main__":
    print("SVG Accessibility Utility")
    print("-----------------------")
    print("1. Process SVGs to add accessibility features")
    print("2. Audit SVGs for accessibility issues")
    print("3. Restore SVGs from backups")
    print("4. Verify specific SVG file")
    print("5. Exit")
    
    while True:
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == "1":
            batch_process_svgs()
        elif choice == "2":
            audit_svg_files()
        elif choice == "3":
            restore_backups()
        elif choice == "4":
            file_path = input("Enter SVG file path: ")
            success, message = verify_svg(file_path)
            print(f"\nVerification result: {'Success' if success else 'Failed'}")
            print(f"Message: {message}")
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Please try again.")