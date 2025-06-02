import re

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

html_content = read_file('templates/index_template.html')
original_length = len(html_content)
print(f"Original HTML length: {original_length}")

# --- 1. Cleanup Voice Assistants Cards ---
# This section should be clean. This logic is just for safety / idempotency.
voice_section_pattern = re.compile(
    r'(<div id="voice-assistants" class="tab-content hidden">\s*<div class="grid grid-cols-1 md:grid-cols-3 gap-8 text-c\s*enter">)'
    r'(.*?)'
    r'(</div>\s*</div>)'
    , re.DOTALL
)

def cleanup_voice_grid_content(match):
    grid_start_tag = match.group(1)
    grid_content = match.group(2)
    grid_end_tag = match.group(3)

    loop_pattern = re.compile(r'{% for feature in voice_assistant_features %}.*?{% endfor %}', re.DOTALL)
    loop_match = loop_pattern.search(grid_content)

    if loop_match:
        extracted_loop = loop_match.group(0).strip()
        if grid_content.strip() == extracted_loop:
            print("Voice assistant section already clean.") # No change needed
            return match.group(0)
        else:
            print(f"Voice assistant section: Replacing content with extracted loop.")
            return f"{grid_start_tag}\n{extracted_loop}\n{grid_end_tag}"
    else:
        print(f"WARNING: Voice assistant Jinja loop not found in its section. Content: <<<{grid_content[:200]}...>>>")
        return match.group(0)

html_content_before_voice = html_content
html_content = voice_section_pattern.sub(cleanup_voice_grid_content, html_content, 1)

if html_content == html_content_before_voice:
    print("Voice assistants section not modified (either clean or main pattern failed).")
else:
    print("Voice assistants section was processed.")

# --- 2. Cleanup Challenges Accordion ---
# This pattern defines the accordion div and ensures it captures everything up to the start of the next major element (Future Trends heading)
accordion_section_pattern = re.compile(
    r'(<div id="accordion" class="space-y-4">)' # Group 1: Start of accordion div
    r'(.*?)' # Group 2: All the messy content
    # Group 3: The end of the accordion's parent div, and the start of the next div (Future Trends)
    # This ensures Group 2 captures everything that needs to be replaced.
    r'(</div>\s*</div>\s*<div>\s*<h3 class="font-bold text-2xl mb-6">{{ challenges_section.future_trends_section_title }}</h3>)',
    re.DOTALL
)

# The clean template for a single accordion loop
clean_accordion_loop_template = """{% for item in challenge_items %}
                            <div class="accordion-item">
                                <button class="accordion-header w-full text-left flex justify-between items-center p-4 bg-white rounded-lg shadow-sm border border-gray-200">
                                    <span class="font-medium">{{ item.title | safe }}</span>
                                    <span class="accordion-icon transform rotate-0 transition-transform">▼</span>
                                </button>
                                <div class="accordion-content hidden p-4 bg-gray-50 rounded-b-lg">
                                    <p class="text-gray-600">{{ item.content }}</p>
                                </div>
                            </div>
                            {% endfor %}"""

def replace_accordion_content(match):
    accordion_div_opening_tag = match.group(1) # This is '<div id="accordion" class="space-y-4">'
    # Group 2 is all the junk we want to replace.
    start_of_next_section_marker = match.group(3) # This is '</div>\s*</div>\s*<div>\s*<h3 class="font-bold text-2xl mb-6">{{ challenges_section.future_trends_section_title }}</h3>'

    print("Challenges accordion: Replacing content with a single clean loop.")
    # We construct the clean accordion section:
    # Start of accordion div + clean loop + end of accordion div (which is the first part of group 3)
    # Group 3 is actually "</div></div><div><h3>..."
    # We need to put back the closing div for the accordion itself, then the rest of group 3
    # The first </div> in group 3 is the one that closes <div id="accordion"...>

    # Correct reconstruction:
    # match.group(1) is <div id="accordion" class="space-y-4">
    # We add the clean loop.
    # Then we need ONE </div> to close the accordion.
    # Then match.group(3) contains the rest (</div> closing parent, opening of next, etc.)
    # However, the pattern for group 3 already includes the first </div> that closes the accordion.
    # Let's adjust the pattern slightly for easier replacement.

    # New strategy: group 3 is JUST the end of the accordion div. Group 4 is the lookahead part.
    # This is safer.
    return f"{accordion_div_opening_tag}\n{clean_accordion_loop_template.strip()}\n{start_of_next_section_marker}"


# Redefine pattern for simpler substitution
accordion_section_pattern_final = re.compile(
    r'(<div id="accordion" class="space-y-4">)' # Group 1: Start of accordion div
    r'(.*?)' # Group 2: All the messy content. THIS WILL BE REPLACED.
    # Group 3: This is what must immediately follow the accordion's true closing div to ensure we have the right scope.
    r'(</div>\s*</div>\s*<div>\s*<h3 class="font-bold text-2xl mb-6">{{ challenges_section.future_trends_section_title }}</h3>)',
    re.DOTALL
)

def replace_accordion_content_final(match):
    start_of_accordion_div = match.group(1) # <div id="accordion" class="space-y-4">
    # The content matched by group(2) is discarded.
    end_of_accordion_and_lookahead = match.group(3) # </div></div><div><h3... (first </div> closes accordion)

    print("Challenges accordion (final attempt): Replacing content with a single clean loop.")
    # The replacement is: start tag + clean loop + the original end part (which includes accordion's own closing div)
    return f"{start_of_accordion_div}\n{clean_accordion_loop_template.strip()}\n{end_of_accordion_and_lookahead}"


html_content_before_accordion = html_content
match_accordion = accordion_section_pattern_final.search(html_content)
if match_accordion:
    # Manually construct the string for replacement
    # Content before the accordion's body + clean loop + content after accordion's body
    start_index = match_accordion.start(2) # Start of group 2 (the messy content)
    end_index = match_accordion.end(2)     # End of group 2

    # Ensure we use the correct parts for reconstruction
    # Group 1: Opening tag of accordion div
    # Group 3: The closing tag of accordion div AND the start of the next section
    # The actual closing tag for the accordion is the first `</div>` in group 3.
    # We need to be careful here. The pattern for group 3 means that group 2 (.*?) ends *before* that first </div>.

    # Simpler: Replace from start of group 2 to end of group 2 with desired content.
    # The entire match includes group1, group2, group3.
    # group1 = <div id="accordion"...>
    # group2 = messy content
    # group3 = </div> (for accordion) </div> (for parent) <div><h3> (for next section)

    # We want: group1 + clean_loop + group3
    # This means the original pattern sub was mostly fine, but the content of group3 needs to be precise.
    # The issue is that group3 needs to be the TRUE end of the accordion div.
    # Let's use the simpler replacement logic from the first successful sections.
    # The key is the pattern for the *entire section* being replaced.

    # Redefine pattern to capture start, content, and end of the specific accordion div
    # This is what I had before, let's re-verify its effect.
    # r'(<div id="accordion" class="space-y-4">)(.*?)(</div>)'
    # If Group 3 (</div>) is too greedy and matches an inner item's </div>, then it fails.
    # The problem is the duplicated loops *also* contain </div>.
    # The current HTML has junk like: <div id="accordion"> loop1 endfor loop2 endfor </div> </div> static_item1 static_item2 </div>
    # The above pattern would match: G1=<div id=accordion> G2=loop1 endfor loop2 endfor G3=</div>.
    # Then it replaces G2 with clean_loop. Result: G1 clean_loop G3. This is correct.
    # The issue is if the *static items* are also within this G1...G3 block somehow.

    # The problem is the stray </div> tags.
    # The HTML: <div id="accordion"> loop loop </div> </div> static1 static2 ...
    # My pattern: (<div id="accordion">) (loop loop) (</div>)
    # Result: <div id="accordion"> CLEAN_LOOP </div> </div> static1 static2 ...
    # This IS what happened. The stray </div> and static items are OUTSIDE the match of this regex.

    # The regex MUST consume the static items as well.
    # It must go from <div id="accordion"...> up to just BEFORE <div> <h3 ... future_trends ...>
    # The parent of "accordion" div:
    # <div class="grid ..."> <div> <h3..key challenges..</h3> <div id="accordion">...</div> </div> <div> <h3..future trends..</h3> ... </div> </div>

    # The content to replace is from the end of ">" of <div id="accordion"...>
    # to the beginning of "</div>" that closes the accordion div.

    final_accordion_replacement_pattern = re.compile(
        r'(<div id="accordion" class="space-y-4">)' # Group 1
        r'.*?' # Group 2 - ALL content until the specific lookahead for its correct closing div
        r'(</div>\s*</div>\s*<div>\s*<h3 class="font-bold text-2xl mb-6">{{ challenges_section.future_trends_section_title }}</h3>)', # Group 3 - Suffix
        re.DOTALL
    )
    # In this pattern, group 2 is all the junk. Group 3 is the suffix that ensures group 2 ends correctly.
    # The replacement should be: group(1) + clean_loop_template + group(3)
    # This means the first </div> of group(3) is implicitly the one that closes group(1).
    # So, we must adjust group(3) to not include the accordion's own closing div, or adjust the replacement.

    # Replacement: G1 + clean_loop + "</div>" (to close G1) + G3_modified (without the first div)

    # Let's try a simpler pattern that should have worked if the HTML wasn't so messy:
    # Replace the innerHTML of the accordion div.
    final_accordion_pattern_for_innerhtml = re.compile(
         r'(<div id="accordion" class="space-y-4">)' # G1
         r'(.*?)' # G2 = inner HTML
         r'(</div>)', # G3 = closing tag
         re.DOTALL
    )
    # To ensure G3 is the *correct* closing tag for G1, not an inner one:
    # We must assume there are no other <div id="accordion"...> nested.
    # The issue is that G2 can be (messy loop) </div> (stray) (static_item) </div> (another stray) (static_item)
    # and G3 will match the first </div> it sees.

    # The most direct way: find <div id="accordion"...> and replace up to where future trends start.
    # This means replacing part of the grid structure.

    # Sticking to the logic: find the accordion div, and replace its content.
    # The problem is that the "content" now includes stray closing divs and static items that are siblings, not children.

    # If the HTML is: <div id="accordion"> A </div> </div> B C </div> <div> <h3 future trends>
    # G1 = <div id="accordion">
    # G2 = A
    # G3 = </div> (closes A)
    # Replacement by script: <div id="accordion"> CLEAN_LOOP </div>. The rest (</div> B C ...) remains. This is the current problem.

    # The script needs to replace from end of G1, up to the start of the "Future Trends" H3's PARENT DIV.
    # Pattern: (<div id="accordion" class="space-y-4">) (.*?) (</div>\s*</div>\s*(<div>\s*<h3 class="font-bold text-2xl mb-6">{{ challenges_section.future_trends_section_title }}</h3>))
    # G1 = <div id="accordion"...>
    # G2 = All the mess (loops, static items, stray divs)
    # G3 = The closing div for accordion's PARENT, and the start of future trends PARENT.
    # Replacement: G1 + clean_loop_template + "</div>" (to close accordion) + G3

    # This should be it:
    replacement_target_pattern = re.compile(
        r'(<div id="accordion" class="space-y-4">)' # G1: Start of accordion div
        r'.*?' # Greedily match all the junk: duplicated loops, static items, stray closing divs
        r'(</div>\s*<div>\s*<h3 class="font-bold text-2xl mb-6">{{ challenges_section.future_trends_section_title }}</h3>)', # G2: Anchor: this is the PARENT div of Future Trends
        re.DOTALL
    )

    def replace_bad_accordion_block(match):
        accordion_opening_tag = match.group(1)
        anchor_for_next_section = match.group(2)
        print("Challenges accordion (final definitive attempt): Replacing messy block with clean loop.")
        # We are replacing everything between the start of the accordion
        # and the start of the div that contains the "Future Trends" heading.
        # The replaced part includes the accordion's own true closing div.
        return f"{accordion_opening_tag}\n{clean_accordion_loop_template.strip()}\n</div>\n{anchor_for_next_section}"

    html_content = replacement_target_pattern.sub(replace_bad_accordion_block, html_content, 1)

else: # Main accordion_section_pattern_final didn't match
    print("Challenges accordion: Main section pattern (accordion_section_pattern_final) did not match. No changes made to accordion.")


if html_content == html_content_before_accordion:
     print("Accordion section was not modified by the sub function for accordion.")
else:
     print("Accordion section was targeted and processed by the sub function for accordion.")


# Final check on content length
if len(html_content) < original_length:
    print(f"SUCCESS: HTML content reduced. Original length: {original_length}, New length: {len(html_content)}")
elif len(html_content) == original_length:
    print("NOTICE: HTML content length unchanged. Check messages above. Could be clean already or patterns didn't match.")
else:
    print(f"HTML content might have changed. Original: {original_length}, New: {len(html_content)}. Review needed if not a reduction.")

write_file('templates/index_template.html', html_content)
print("Template cleanup script finished.")
