import re

def read_file(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

html_content = read_file('templates/index_template.html')

# --- Global Content ---
html_content = html_content.replace(
    '<title>人工智能融入日常：交互式调研报告</title>',
    '<title>{{ global_content.page_title }}</title>'
)
html_content = html_content.replace(
    '<a href="#hero" class="text-xl font-bold text-[#4A6C6F]">AI 融入日常</a>',
    '<a href="#hero" class="text-xl font-bold text-[#4A6C6F]">{{ global_content.header_brand_text }}</a>'
)
html_content = html_content.replace(
    '<p>&copy; 2025 AI融入日常调研报告。基于源报告数据生成的可视化应用。</p>',
    '<p>{{ global_content.footer_copyright_text | safe }}</p>'
)

# --- Nav Links ---
nav_pattern = re.compile(r'(<div class="hidden md:block">\s*<div class="ml-10 flex items-baseline space-x-4">)(.*?)(</div>\s*</div>)', re.DOTALL)
mobile_nav_pattern = re.compile(r'(<div id="mobile-menu" class="md:hidden hidden">\s*<div class="px-2 pt-2 pb-3 space-y-1 sm:px-3">)(.*?)(</div>\s*</div>)', re.DOTALL)
nav_replacement_template = r'''{% for link in nav_links %}
                        <a href="{{ link.href }}" class="nav-link px-3 py-2 rounded-md text-sm font-medium">{{ link.text }}</a>
                        {% endfor %}'''
mobile_nav_replacement_template = r'''{% for link in nav_links %}
                <a href="{{ link.href }}" class="block nav-link px-3 py-2 rounded-md text-base font-medium">{{ link.text }}</a>
                {% endfor %}'''
html_content = nav_pattern.sub(r'\1' + nav_replacement_template + r'\3', html_content, 1)
html_content = mobile_nav_pattern.sub(r'\1' + mobile_nav_replacement_template + r'\3', html_content, 1)

# --- Hero Section ---
html_content = html_content.replace(
    '<span class="text-[#4A6C6F]">人工智能</span> 已融入日常生活', # Original static text
    '<span class="text-[#4A6C6F]">{{ hero.title_part1 }}</span> {{ hero.title_part2 }}'
)
hero_subtitle_original = """本报告深入调研AI在2025年如何实际切入普通人的生活。从聊天、创作到工作与健康，AI正以前所未有的方式提升效率、激
发创造力并重塑我们的世界。""" # Note the exact newline from original
html_content = html_content.replace(hero_subtitle_original, '{{ hero.subtitle }}')

# Hero Buttons - Target original full anchor tags for link replacement, then replace text content
hero_button1_original_full_link = """<a href="#insights" class="bg-[#4A6C6F] text-white font-bold py-3 px-8 rounded-full hover:bg-[#3E5A5D] transition-colors">"""
hero_button1_replacement_link = """<a href="{{ hero.button1_link }}" class="bg-[#4A6C6F] text-white font-bold py-3 px-8 rounded-full hover:bg-[#3E5A5D] transition-colors">"""
html_content = html_content.replace(hero_button1_original_full_link, hero_button1_replacement_link)
html_content = html_content.replace(
    """查看核心数据
                    </a>""",
    """{{ hero.button1_text }}
                    </a>"""
)

hero_button2_original_full_link = """<a href="#assistants" class="bg-gray-200 text-gray-800 font-bold py-3 px-8 rounded-full hover:bg-gray-300 transition-colors">"""
hero_button2_replacement_link = """<a href="{{ hero.button2_link }}" class="bg-gray-200 text-gray-800 font-bold py-3 px-8 rounded-full hover:bg-gray-300 transition-colors">"""
html_content = html_content.replace(hero_button2_original_full_link, hero_button2_replacement_link)
html_content = html_content.replace(
    """探索AI应用
                    </a>""",
    """{{ hero.button2_text }}
                    </a>"""
)

# --- Section Titles & Subtitles (using exact original strings) ---
html_content = html_content.replace(
    '<h2 class="text-3xl font-bold tracking-tight sm:text-4xl">\n对话式AI：您的数字助手</h2>',
    '<h2 class="text-3xl font-bold tracking-tight sm:text-4xl">\n{{ assistants_section.title }}</h2>'
)
html_content = html_content.replace(
    '<p class="mt-4 text-lg text-gray-600 max-w-2xl mx-auto">AI\n助手通过自然语言交互，帮助我们获取信息、自动执行任务，已成为不可或缺的数字伴侣。</p>',
    '<p class="mt-4 text-lg text-gray-600 max-w-2xl mx-auto">{{ assistants_section.subtitle }}</p>'
)
html_content = html_content.replace(
    '<button data-tab="chatbots" class="tab-button active tex\nt-gray-700 py-3 px-6 block font-medium text-center focus:outline-none">\n                            聊天机器人\n                        </button>',
    '<button data-tab="chatbots" class="tab-button active text-gray-700 py-3 px-6 block font-medium text-center focus:outline-none">\n                            {{ assistants_section.tab1_title }}\n                        </button>'
)
html_content = html_content.replace(
    '<button data-tab="voice-assistants" class="tab-button te\nxt-gray-700 py-3 px-6 block font-medium text-center focus:outline-none">\n                            语音助手\n                        </button>',
    '<button data-tab="voice-assistants" class="tab-button text-gray-700 py-3 px-6 block font-medium text-center focus:outline-none">\n                            {{ assistants_section.tab2_title }}\n                        </button>'
)
html_content = html_content.replace(
    '<h2 class="text-3xl font-bold tracking-tight sm:text-4xl">AI\n创作：释放全民创造力</h2>',
    '<h2 class="text-3xl font-bold tracking-tight sm:text-4xl">{{ creativity_section.title }}</h2>'
)
html_content = html_content.replace(
    '<p class="mt-4 text-lg text-gray-600 max-w-2xl mx-auto">从图\n像到声音，生成式AI正在使内容创作大众化，让每个人都能成为创作者。</p>',
    '<p class="mt-4 text-lg text-gray-600 max-w-2xl mx-auto">{{ creativity_section.subtitle }}</p>'
)
html_content = html_content.replace(
    '<h2 class="text-3xl font-bold tracking-tight sm:text-4xl">AI\n生活：无处不在的智能</h2>',
    '<h2 class="text-3xl font-bold tracking-tight sm:text-4xl">{{ lifestyle_section.title }}</h2>'
)
html_content = html_content.replace(
    '<p class="mt-4 text-lg text-gray-600 max-w-2xl mx-auto">AI\n正巧妙地融入我们日常使用的应用和设备中，在幕后提升效率，提供个性化体验。</p>',
    '<p class="mt-4 text-lg text-gray-600 max-w-2xl mx-auto">{{ lifestyle_section.subtitle }}</p>'
)
html_content = html_content.replace(
    '<h2 class="text-3xl font-bold tracking-tight sm:text-4xl">\n数据洞察：AI采纳现状</h2>',
    '<h2 class="text-3xl font-bold tracking-tight sm:text-4xl">\n{{ insights_section.title }}</h2>'
)
html_content = html_content.replace(
    '<p class="mt-4 text-lg text-gray-600 max-w-2xl mx-auto">统计\n数据揭示了生成式AI在全球的普及程度、用户特征以及人们对这项技术的看法。</p>',
    '<p class="mt-4 text-lg text-gray-600 max-w-2xl mx-auto">{{ insights_section.subtitle }}</p>'
)
html_content = html_content.replace(
    '<h3 class="font-bold text-2xl mb-4 text-center">生成式AI使\n用率 (部分国家)</h3>',
    '<h3 class="font-bold text-2xl mb-4 text-center">{{ insights_section.chart1_title }}</h3>'
)
html_content = html_content.replace(
    '<h3 class="font-bold text-2xl mb-4 text-center">AI用户年龄\n分布</h3>',
    '<h3 class="font-bold text-2xl mb-4 text-center">{{ insights_section.chart2_title }}</h3>'
)
html_content = html_content.replace(
    '<h2 class="text-3xl font-bold tracking-tight sm:text-4xl">\n挑战与未来</h2>',
    '<h2 class="text-3xl font-bold tracking-tight sm:text-4xl">\n{{ challenges_section.title }}</h2>'
)
html_content = html_content.replace(
    '<p class="mt-4 text-lg text-gray-600 max-w-2xl mx-auto">AI\n的广泛应用带来了隐私、偏见等伦理挑战，同时也预示着代理式AI等多项激动人心的未来趋势。</p>',
    '<p class="mt-4 text-lg text-gray-600 max-w-2xl mx-auto">{{ challenges_section.subtitle }}</p>'
)
html_content = html_content.replace(
    '<h3 class="font-bold text-2xl mb-6">关键挑战</h3>',
    '<h3 class="font-bold text-2xl mb-6">{{ challenges_section.accordion_section_title }}</h3>'
)
html_content = html_content.replace(
    '<h3 class="font-bold text-2xl mb-6">未来趋势</h3>',
    '<h3 class="font-bold text-2xl mb-6">{{ challenges_section.future_trends_section_title }}</h3>'
)

# --- Card and List Sections (using container replacement strategy) ---
chatbot_container_pattern = re.compile(r'(<div id="chatbots" class="tab-content">\s*<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">)(.*?)(</div>\s*</div>)', re.DOTALL)
chatbot_card_template = r'''{% for card in assistant_cards_chatbots %}
                            <div class="card p-6 rounded-lg">
                                <h3 class="font-bold text-xl mb-2">{{ card.title }}</h3>
                                <p class="text-gray-600 mb-4">{{ card.description }}</p>
                                <span class="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full {{ card.badge_style | default('text-green-600 bg-green-200') }}">{{ card.badge_text }}</span>
                            </div>
                            {% endfor %}'''
html_content = chatbot_container_pattern.sub(r'\1' + chatbot_card_template + r'\2', html_content, 1)

voice_cards_pattern = re.compile(r'(<div id="voice-assistants" class="tab-content hidden">\s*<div class="grid grid-cols-1 md:grid-cols-3 gap-8 text-c\s*enter">)(.*?)(</div>\s*</div>)', re.DOTALL)
voice_card_template = r'''{% for feature in voice_assistant_features %}
                            <div class="card p-6 rounded-lg">
                                <div class="text-4xl mb-4 text-[#D4AF37]">{{ feature.icon }}</div>
                                <h3 class="font-bold text-xl mb-2">{{ feature.title }}</h3>
                                <p class="text-gray-600">{{ feature.description }}</p>
                            </div>
                            {% endfor %}'''
html_content = voice_cards_pattern.sub(r'\1' + voice_card_template + r'\2', html_content, 1)

creativity_cards_pattern = re.compile(r'(<section id="creativity" class="py-16 md:py-24 bg-white">.*?<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8\s*">)(.*?)(</div>\s*</div>\s*</section>)', re.DOTALL)
creativity_card_template = r'''{% for card in creativity_cards %}
                    <div class="card p-6 rounded-lg">
                         <div class="flex justify-between items-start">
                             <h3 class="font-bold text-xl mb-2">{{ card.title }}</h3>
                             <span class="text-2xl">{{ card.icon_emoji }}</span>
                         </div>
                        <p class="text-gray-600 mb-4">{{ card.description }}</p>
                        <div class="mt-4 pt-4 border-t border-gray-200">
                             <p class="text-sm text-red-600"><span class="font-bold">伦理警示:</span> {{ card.ethical_warning }}</p>
                        </div>
                    </div>
                    {% endfor %}'''
html_content = creativity_cards_pattern.sub(r'\1' + creativity_card_template + r'\3', html_content, 1)

lifestyle_cards_pattern = re.compile(r'(<section id="lifestyle" class="py-16 md:py-24">.*?<div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-8\s*">)(.*?)(</div>\s*</div>\s*</section>)', re.DOTALL)
lifestyle_card_template = r'''{% for card in lifestyle_cards %}
                    <div class="card p-6 rounded-lg text-center">
                        <div class="text-4xl mb-4">{{ card.icon_emoji }}</div>
                        <h4 class="font-semibold text-lg">{{ card.title }}</h4>
                        <p class="text-sm text-gray-500 mt-2">{{ card.description }}</p>
                    </div>
                    {% endfor %}'''
html_content = lifestyle_cards_pattern.sub(r'\1' + lifestyle_card_template + r'\3', html_content, 1)

challenge_container_pattern = re.compile(r'(<div id="accordion" class="space-y-4">)(.*?)(</div>)', re.DOTALL)
challenge_item_template = r'''{% for item in challenge_items %}
                            <div class="accordion-item">
                                <button class="accordion-header w-full text-left flex justify-between items-center p-4 bg-white rounded-lg shadow-sm border border-gray-200">
                                    <span class="font-medium">{{ item.title | safe }}</span>
                                    <span class="accordion-icon transform rotate-0 transition-transform">▼</span>
                                </button>
                                <div class="accordion-content hidden p-4 bg-gray-50 rounded-b-lg">
                                    <p class="text-gray-600">{{ item.content }}</p>
                                </div>
                            </div>
                            {% endfor %}'''
# This replacement should target the content of the accordion, between its opening and closing tags.
html_content = challenge_container_pattern.sub(r'\1' + challenge_item_template + r'\2', html_content, 1)


future_trends_pattern = re.compile(r'(<ul class="space-y-4">)(.*?)(</ul>)', re.DOTALL)
future_trend_template = r'''{% for trend in future_trends %}
                            <li class="card p-4 flex items-center space-x-4 rounded-lg">
                                <span class="text-2xl">{{ trend.icon_emoji }}</span>
                                <div>
                                    <h4 class="font-semibold">{{ trend.title }}</h4>
                                    <p class="text-sm text-gray-600">{{ trend.description }}</p>
                                </div>
                            </li>
                            {% endfor %}'''
html_content = future_trends_pattern.sub(r'\1' + future_trend_template + r'\2', html_content, 1)

# --- Chart Script Injection ---
adoption_chart_data_pattern = re.compile(
    r"(new Chart\(ctxAdoption, \{.*?data: \{)(.*?)(,\s*options:)", re.DOTALL
)
adoption_chart_data_replacement = r"""labels: {{ adoption_chart.labels_json | safe }},
                        datasets: [\{
                            label: '{{ adoption_chart.dataset_label }}',
                            data: {{ adoption_chart.data_json | safe }},
                            backgroundColor: ['#60A5FA', '#FBBF24', '#34D399', '#F87171'],
                            borderColor: ['#3B82F6', '#F59E0B', '#10B981', '#EF4444'],
                            borderWidth: 1
                        }]"""
html_content = adoption_chart_data_pattern.sub(r'\1' + adoption_chart_data_replacement + r'\3', html_content, 1)

demographics_chart_data_pattern = re.compile(
    r"(new Chart\(ctxDemographics, \{.*?data: \{)(.*?)(,\s*options:)", re.DOTALL
)
demographics_chart_data_replacement = r"""labels: {{ demographics_chart.labels_json | safe }},
                        datasets: [\{
                            label: '{{ demographics_chart.dataset_label }}',
                            data: {{ demographics_chart.data_json | safe }},
                            backgroundColor: [
                                'rgba(74, 108, 111, 0.7)',
                                'rgba(212, 175, 55, 0.7)',
                            ],
                            borderColor: [
                                'rgba(74, 108, 111, 1)',
                                'rgba(212, 175, 55, 1)',
                            ],
                            borderWidth: 1
                        }]"""
html_content = demographics_chart_data_pattern.sub(r'\1' + demographics_chart_data_replacement + r'\3', html_content, 1)

write_file('templates/index_template.html', html_content)
print('Template transformation complete (attempt 3).')
