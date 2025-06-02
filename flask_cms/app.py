from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Change this in a real app
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' # Using SQLite for simplicity
db = SQLAlchemy(app)

# ---- Database Models ----

class GlobalContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    page_title = db.Column(db.String(200), default='人工智能融入日常：交互式调研报告')
    header_brand_text = db.Column(db.String(100), default='AI 融入日常')
    footer_copyright_text = db.Column(db.String(300), default='&copy; 2025 AI融入日常调研报告。基于源报告数据生成的可视化应用。')

class NavLink(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(50), nullable=False)
    href = db.Column(db.String(50), nullable=False)
    order = db.Column(db.Integer, default=0) # For ordering if needed

class HeroSection(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title_part1 = db.Column(db.String(100), default='人工智能')
    title_part2 = db.Column(db.String(100), default='已融入日常生活')
    subtitle = db.Column(db.Text, default='本报告深入调研AI在2025年如何实际切入普通人的生活。从聊天、创作到工作与健康，AI正以前所未有的方式提升效率、激发创造力并重塑我们的世界。')
    button1_text = db.Column(db.String(50), default='查看核心数据')
    button1_link = db.Column(db.String(50), default='#insights')
    button2_text = db.Column(db.String(50), default='探索AI应用')
    button2_link = db.Column(db.String(50), default='#assistants')

class AssistantsSectionContent(db.Model): # For the main title/subtitle of the section
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), default='对话式AI：您的数字助手')
    subtitle = db.Column(db.Text, default='AI 助手通过自然语言交互，帮助我们获取信息、自动执行任务，已成为不可或缺的数字伴侣。')
    tab1_title = db.Column(db.String(50), default='聊天机器人')
    tab2_title = db.Column(db.String(50), default='语音助手')

class AssistantCard(db.Model): # For cards under "聊天机器人" tab
    id = db.Column(db.Integer, primary_key=True)
    tab_category = db.Column(db.String(50), default='chatbots') # 'chatbots' or 'voice-assistants'
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    badge_text = db.Column(db.String(100)) # e.g., "优点: 深度研究" or emoji for voice
    # For simplicity, badge_color_class can be predefined in template based on category or title
    # Or, add a field: badge_style = db.Column(db.String(100))
    order = db.Column(db.Integer, default=0)

class VoiceAssistantFeature(db.Model): # For cards under "语音助手" tab specifically
    id = db.Column(db.Integer, primary_key=True)
    icon = db.Column(db.String(10), nullable=False) # Emoji
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)


class CreativitySectionContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), default='AI 创作：释放全民创造力')
    subtitle = db.Column(db.Text, default='从图像到声音，生成式AI正在使内容创作大众化，让每个人都能成为创作者。')

class CreativityCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    icon_emoji = db.Column(db.String(10)) # e.g., "🎨"
    description = db.Column(db.Text)
    ethical_warning = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)

class LifestyleSectionContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), default='AI 生活：无处不在的智能')
    subtitle = db.Column(db.Text, default='AI 正巧妙地融入我们日常使用的应用和设备中，在幕后提升效率，提供个性化体验。')

class LifestyleCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    icon_emoji = db.Column(db.String(10)) # e.g., "💼"
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)

class InsightsSectionContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), default='数据洞察：AI采纳现状')
    subtitle = db.Column(db.Text, default='统计数据揭示了生成式AI在全球的普及程度、用户特征以及人们对这项技术的看法。')
    chart1_title = db.Column(db.String(100), default='生成式AI使用率 (部分国家)')
    chart2_title = db.Column(db.String(100), default='AI用户年龄分布')

class ChartData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    chart_name = db.Column(db.String(100), unique=True, nullable=False) # e.g., 'adoptionRateChart'
    # Storing complex data like labels and values as JSON string
    labels_json = db.Column(db.Text, default='[]') # JSON string for labels
    data_json = db.Column(db.Text, default='[]')   # JSON string for data values
    dataset_label = db.Column(db.String(100), default='Dataset')

class ChallengesSectionContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), default='挑战与未来')
    subtitle = db.Column(db.Text, default='AI 的广泛应用带来了隐私、偏见等伦理挑战，同时也预示着代理式AI等多项激动人心的未来趋势。')
    accordion_section_title = db.Column(db.String(100), default='关键挑战')
    future_trends_section_title = db.Column(db.String(100), default='未来趋势')

class ChallengeItem(db.Model): # Accordion items
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False) # Includes emoji
    content = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)

class FutureTrend(db.Model): # List items for future trends
    id = db.Column(db.Integer, primary_key=True)
    icon_emoji = db.Column(db.String(10))
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    order = db.Column(db.Integer, default=0)

# ---- End Database Models ----

# Function to create database tables
def create_db():
    with app.app_context():
        db.create_all()
        print("Database tables created (if they didn't exist).")

# Placeholder for initial data seeding function
def seed_initial_data():
    with app.app_context():
        # This is where we'll add default data later
        pass
    print("Initial data seeding placeholder.")

# Command to initialize database (can be called via flask shell or a CLI command)
# For now, we can call it directly for setup if __name__ == '__main__'
# Or better, create a flask cli command.

# Example of how to add a CLI command to create DB (optional for now, but good practice)
# @app.cli.command('init-db')
# def init_db_command():
#     create_db()
#     seed_initial_data()
#     print('Initialized the database and seeded initial data.')

@app.route('/')
def home():
    # This will eventually fetch dynamic content
    return render_template('index_template.html', title='AI an der Tagesordnung')

if __name__ == '__main__':
    app.run(debug=True)
