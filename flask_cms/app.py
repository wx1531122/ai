from flask import Blueprint, Flask, flash, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, IntegerField
from wtforms.validators import DataRequired, Length, Optional
import json

app = Flask(__name__)

# Ensure app config has a decent secret key for Flask-Login
if not app.config.get('SECRET_KEY') or app.config.get('SECRET_KEY') == 'your_secret_key':
    print("WARNING: Using a default or weak SECRET_KEY. Generating a new one for this session.")
    app.config['SECRET_KEY'] = os.urandom(24).hex()

# Initialize Flask-Login with the app instance
login_manager.init_app(app)
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

from sqlalchemy.exc import IntegrityError # For handling cases where data might already exist if run multiple times
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os
# import json # json is already imported globally at the top of app.py

# ---- Initial Data Seeding Function ----
def seed_initial_data():
    with app.app_context():
        # Check if data already exists to prevent duplicate seeding (e.g. by checking GlobalContent)
        if GlobalContent.query.first() is not None:
            print("Database already appears to be seeded. Skipping seed_initial_data.")
            return

        print("Seeding database with initial content from seed_initial_data function...")
        try:
            # Global Content
            global_content = GlobalContent(
                page_title='人工智能融入日常：交互式调研报告',
                header_brand_text='AI 融入日常',
                footer_copyright_text='&copy; 2025 AI融入日常调研报告。基于源报告数据生成的可视化应用。'
            )
            db.session.add(global_content)

            # Nav Links
            nav_items = [
                {'text': 'AI助手', 'href': '#assistants', 'order': 1},
                {'text': 'AI创作', 'href': '#creativity', 'order': 2},
                {'text': 'AI生活', 'href': '#lifestyle', 'order': 3},
                {'text': '数据洞察', 'href': '#insights', 'order': 4},
                {'text': '挑战与未来', 'href': '#challenges', 'order': 5}
            ]
            for item_data in nav_items: db.session.add(NavLink(**item_data))

            # Hero Section
            hero_section = HeroSection(
                title_part1='人工智能', title_part2='已融入日常生活',
                subtitle='本报告深入调研AI在2025年如何实际切入普通人的生活。从聊天、创作到工作与健康，AI正以前所未有的方式提升效率、激发创造力并重塑我们的世界。',
                button1_text='查看核心数据', button1_link='#insights',
                button2_text='探索AI应用', button2_link='#assistants'
            )
            db.session.add(hero_section)

            # Assistants Section Content
            assistants_section_content = AssistantsSectionContent(
                title='对话式AI：您的数字助手',
                subtitle='AI 助手通过自然语言交互，帮助我们获取信息、自动执行任务，已成为不可或缺的数字伴侣。',
                tab1_title='聊天机器人', tab2_title='语音助手'
            )
            db.session.add(assistants_section_content)

            # Assistant Cards (Chatbots)
            chatbot_cards_data = [
                {'title': 'ChatGPT (OpenAI)', 'description': '功能强大的研究、问题解决和写作工具。普通用户用它进行创意写作、学习和编程辅助。', 'badge_text': '优点: 深度研究', 'order': 1},
                {'title': 'Google Gemini', 'description': '与Google Workspace深度集成，擅长复杂推理和文件处理，可简化邮件、日程管理等任务。', 'badge_text': '优点: 生态集成', 'order': 2},
                {'title': 'Microsoft Copilot', 'description': '结合Bing搜索提供最新信息，与Microsoft 365无缝结合，辅助文档、表格和演示稿创作。', 'badge_text': '优点: 实时信息', 'order': 3},
                {'title': 'Meta AI', 'description': '集成于主流社交应用，扮演个人助理、旅行规划和内容生成器等多种角色。', 'badge_text': '优点: 社交便利', 'order': 4},
                {'title': 'Claude (Anthropic)', 'description': '在编码任务和基于上下文的协作方面表现突出，注重模型的可靠性与安全性。', 'badge_text': '优点: 编码强大', 'order': 5},
                {'title': 'Perplexity AI', 'description': 'AI驱动的搜索引擎，提供带引用来源的实时答案，尤其适合深度研究和信息核查。', 'badge_text': '优点: 精准溯源', 'order': 6}
            ]
            for data in chatbot_cards_data: db.session.add(AssistantCard(tab_category='chatbots', **data))

            # Voice Assistant Features
            voice_features_data = [
                {'icon': '🗣️', 'title': '日常任务', 'description': '查询天气、播放音乐、设置闹钟、发送消息。全球20.5%的人使用语音搜索。', 'order': 1},
                {'icon': '🏠', 'title': '智能家居控制', 'description': '控制灯光、恒温器等智能设备，是语音助手普及的主要驱动力。', 'order': 2},
                {'icon': '🛒', 'title': '购物与导航', 'description': '查找路线、进行预订、购买日常用品。76%的语音搜索是“我附近的”查询。', 'order': 3}
            ]
            for data in voice_features_data: db.session.add(VoiceAssistantFeature(**data))

            # Creativity Section Content
            creativity_section_content = CreativitySectionContent(title='AI 创作：释放全民创造力', subtitle='从图像到声音，生成式AI正在使内容创作大众化，让每个人都能成为创作者。')
            db.session.add(creativity_section_content)

            # Creativity Cards
            creativity_cards_data = [
                {'title': '文生图', 'icon_emoji': '🎨', 'description': '通过文本描述创作图像。Midjourney以艺术风格著称，DALL-E 3擅长理解细节，Stable Diffusion开源灵活。', 'ethical_warning': '版权、风格复制和深度伪造是主要担忧。', 'order': 1},
                {'title': '文生声音/语音', 'icon_emoji': '🎤', 'description': '创建逼真的配音和旁白。ElevenLabs以其超逼真语音闻名，Murf AI提供庞大的语音库。', 'ethical_warning': '语音克隆技术可能被用于身份冒充和欺诈。', 'order': 2},
                {'title': 'AI视频编辑', 'icon_emoji': '🎬', 'description': '简化视频创作流程。Descript通过编辑文本来剪辑视频，Google Vids能将幻灯片转为视频。', 'ethical_warning': '高质量AI生成视频仍处早期，连贯性是挑战。', 'order': 3}
            ]
            for data in creativity_cards_data: db.session.add(CreativityCard(**data))

            # Lifestyle Section Content
            lifestyle_section_content = LifestyleSectionContent(title='AI 生活：无处不在的智能', subtitle='AI 正巧妙地融入我们日常使用的应用和设备中，在幕后提升效率，提供个性化体验。')
            db.session.add(lifestyle_section_content)

            # Lifestyle Cards
            lifestyle_cards_data = [
                {'icon_emoji': '💼', 'title': '工作学习', 'description': 'M365 Copilot和Google Gemini辅助文档处理、数据分析和会议纪要。', 'order': 1},
                {'icon_emoji': '🛒', 'title': '购物体验', 'description': 'Amazon和Shopify等平台利用AI提供个性化推荐和智能客服。', 'order': 2},
                {'icon_emoji': '🎓', 'title': '教育创新', 'description': 'Duolingo和可汗学院利用AI提供个性化辅导和自适应学习路径。', 'order': 3},
                {'icon_emoji': '🏠', 'title': '智能家居', 'description': '智能恒温器、照明和安防系统通过学习用户习惯，实现自动化控制。', 'order': 4},
                {'icon_emoji': '❤️', 'title': '健康关怀', 'description': '可穿戴设备和App通过AI分析健康数据，提供个性化健身与心理支持。', 'order': 5},
                {'icon_emoji': '🔍', 'title': '智能搜索', 'description': 'Google和Bing的AI模式提供更具对话性和个性化的搜索体验。', 'order': 6},
                {'icon_emoji': '✍️', 'title': '写作辅助', 'description': 'Grammarly等工具检查语法、风格和清晰度，提升写作质量。', 'order': 7},
                {'icon_emoji': '📱', 'title': '社交媒体', 'description': 'AI算法驱动着TikTok、Instagram等平台的内容推送和推荐。', 'order': 8}
            ]
            for data in lifestyle_cards_data: db.session.add(LifestyleCard(**data))

            # Insights Section Content
            insights_section_content = InsightsSectionContent(
                title='数据洞察：AI采纳现状',
                subtitle='统计数据揭示了生成式AI在全球的普及程度、用户特征以及人们对这项技术的看法。',
                chart1_title='生成式AI使用率 (部分国家)',
                chart2_title='AI用户年龄分布'
            )
            db.session.add(insights_section_content)

            # ChartData
            adoption_chart = ChartData(chart_name='adoptionRateChart', labels_json=json.dumps(['印度', '澳大利亚', '美国', '英国']), data_json=json.dumps([73, 49, 45, 29]), dataset_label='生成式AI使用率 (%)')
            db.session.add(adoption_chart)
            demographics_chart = ChartData(chart_name='demographicsChart', labels_json=json.dumps(['千禧一代 & Z世代', 'X世代 & 婴儿潮一代']), data_json=json.dumps([65, 35]), dataset_label='用户分布')
            db.session.add(demographics_chart)

            # Challenges Section Content
            challenges_section_content = ChallengesSectionContent(
                title='挑战与未来',
                subtitle='AI 的广泛应用带来了隐私、偏见等伦理挑战，同时也预示着代理式AI等多项激动人心的未来趋势。',
                accordion_section_title='关键挑战',
                future_trends_section_title='未来趋势'
            )
            db.session.add(challenges_section_content)

            # Challenge Items (Accordion)
            challenge_items_data = [
                {'title': '🛡️ 隐私与数据安全', 'content': 'AI系统依赖海量数据，引发了对数据滥用、监控和黑客攻击的担忧。用户的交互内容可能被收集用于模型训练。', 'order': 1},
                {'title': '⚖️ 偏见与公平性', 'content': '训练数据中存在的偏见可能被AI模型复制甚至放大，导致在招聘、信贷等领域出现歧视性结果。', 'order': 2},
                {'title': '📰 虚假信息与深度伪造', 'content': 'AI降低了制造逼真虚假信息（文本、图像、音视频）的门槛，对社会信任和民主进程构成威胁。', 'order': 3},
                {'title': '🧠 过度依赖与批判性思维', 'content': '长期依赖AI完成思考和决策任务，可能削弱用户的独立思考、问题解决和批判性评估能力。', 'order': 4}
            ]
            for data in challenge_items_data: db.session.add(ChallengeItem(**data))

            # Future Trends
            future_trends_data = [
                {'icon_emoji': '🤖', 'title': '代理式AI (Agentic AI)', 'description': 'AI将从执行指令的工具演变为能自主规划并执行多步骤复杂任务的智能代理。', 'order': 1},
                {'icon_emoji': '🧩', 'title': '多模态AI深化应用', 'description': 'AI将更擅长同时理解和生成文本、图像、音频、视频等多种信息，交互更自然。', 'order': 2},
                {'icon_emoji': '🔬', 'title': '科学与机器人领域拓展', 'description': 'AI将在科学发现和机器人技术中发挥更大作用，并逐渐渗透到消费级产品。', 'order': 3}
            ]
            for data in future_trends_data: db.session.add(FutureTrend(**data))

            db.session.commit()
            print("Database seeded successfully by seed_initial_data function.")
        except IntegrityError: # Catch if trying to add duplicate data, e.g. unique constraint violated
            db.session.rollback()
            print("Database already seeded or unique constraint violated (IntegrityError in seed_initial_data).")
        except Exception as e:
            db.session.rollback() # Rollback on any other error during seeding
            print(f"Error seeding database in seed_initial_data: {e}")

# End of seed_initial_data function

# Command to initialize database (can be called via flask shell or a CLI command)
# For now, we can call it directly for setup if __name__ == '__main__'
# Or better, create a flask cli command.

# Example of how to add a CLI command to create DB (optional for now, but good practice)
#
# ---- Admin Setup ----
# Prepend these imports if they don't exist (some might overlap)

# Ensure app config has a decent secret key
# This code will be part of what's injected into app.py's scope where 'app' is defined.
# It needs to be executed after 'app = Flask(__name__)'
# The modifier script will place this block of code correctly.

# Flask-Login setup
login_manager = LoginManager()
# login_manager.init_app(app) # This will be handled by the modifier script after app is available
login_manager.login_view = 'admin_bp.login' # Route name for the login page
login_manager.login_message_category = 'info'

# In-memory user store (for simplicity in this step)
users = {
    "admin": {"password_hash": generate_password_hash("adminpass")}
}

class User(UserMixin):
    def __init__(self, id):
        self.id = id
        self.password_hash = users.get(id, {}).get("password_hash")

    @staticmethod
    def get(user_id):
        if user_id in users:
            return User(user_id)
        return None

@login_manager.user_loader
def load_user(user_id):
    return User.get(user_id)

# Admin Blueprint
admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin', template_folder='templates/admin')

@admin_bp.route('/')
@login_required
def dashboard():
    return render_template('admin_dashboard.html', title="Admin Dashboard")

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_bp.dashboard'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.get(username)
        if user and user.password_hash and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('admin_bp.dashboard'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title="Admin Login")

@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin_bp.login'))

class GlobalContentForm(FlaskForm):
    page_title = StringField('Page Title', validators=[DataRequired(), Length(min=5, max=200)])
    header_brand_text = StringField('Header Brand Text', validators=[DataRequired(), Length(min=3, max=100)])
    footer_copyright_text = TextAreaField('Footer Copyright Text', validators=[DataRequired(), Length(min=10, max=300)])
    submit = SubmitField('Update Global Content')

@admin_bp.route('/edit_global_content', methods=['GET', 'POST'])
@login_required
def edit_global_content():
    # GlobalContent is expected to be a single record.
    content = GlobalContent.query.first()
    if not content:
        flash('Error: GlobalContent record not found. Please ensure database is seeded.', 'danger')
        return redirect(url_for('admin_bp.dashboard'))

    form = GlobalContentForm(obj=content) # Load existing data into the form

    if form.validate_on_submit():
        content.page_title = form.page_title.data
        content.header_brand_text = form.header_brand_text.data
        content.footer_copyright_text = form.footer_copyright_text.data
        try:
            db.session.commit()
            flash('Global content updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating global content: {str(e)}', 'danger')
        return redirect(url_for('admin_bp.edit_global_content')) # Redirect back to the same edit page

    return render_template('admin/edit_global_content.html', title="Edit Global Content", form=form)

class HeroSectionForm(FlaskForm):
    title_part1 = StringField('Title Part 1', validators=[DataRequired(), Length(max=100)])
    title_part2 = StringField('Title Part 2', validators=[DataRequired(), Length(max=100)])
    subtitle = TextAreaField('Subtitle', validators=[DataRequired(), Length(max=1000)])
    button1_text = StringField('Button 1 Text', validators=[DataRequired(), Length(max=50)])
    button1_link = StringField('Button 1 Link (e.g., #insights or /page)', validators=[DataRequired(), Length(max=100)])
    button2_text = StringField('Button 2 Text', validators=[DataRequired(), Length(max=50)])
    button2_link = StringField('Button 2 Link (e.g., #assistants or /page)', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Update Hero Section')

@admin_bp.route('/edit_hero_section', methods=['GET', 'POST'])
@login_required
def edit_hero_section():
    content = HeroSection.query.first()
    if not content:
        flash('Error: HeroSection record not found. Please ensure database is seeded.', 'danger')
        return redirect(url_for('admin_bp.dashboard'))

    form = HeroSectionForm(obj=content)

    if form.validate_on_submit():
        content.title_part1 = form.title_part1.data
        content.title_part2 = form.title_part2.data
        content.subtitle = form.subtitle.data
        content.button1_text = form.button1_text.data
        content.button1_link = form.button1_link.data
        content.button2_text = form.button2_text.data
        content.button2_link = form.button2_link.data
        try:
            db.session.commit()
            flash('Hero Section updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating Hero Section: {str(e)}', 'danger')
        return redirect(url_for('admin_bp.edit_hero_section'))

    return render_template('admin/edit_hero_section.html', title="Edit Hero Section", form=form)

# --- AssistantsSectionContent ---
class AssistantsSectionContentForm(FlaskForm):
    title = StringField('Section Title', validators=[DataRequired(), Length(max=100)])
    subtitle = TextAreaField('Section Subtitle', validators=[DataRequired(), Length(max=1000)])
    tab1_title = StringField('Tab 1 Title (e.g., Chatbots)', validators=[DataRequired(), Length(max=50)])
    tab2_title = StringField('Tab 2 Title (e.g., Voice Assistants)', validators=[DataRequired(), Length(max=50)])
    submit = SubmitField('Update Assistants Section Content')

@admin_bp.route('/edit_assistants_section_content', methods=['GET', 'POST'])
@login_required
def edit_assistants_section_content():
    content = AssistantsSectionContent.query.first()
    if not content:
        flash('Error: AssistantsSectionContent not found.', 'danger')
        return redirect(url_for('admin_bp.dashboard'))
    form = AssistantsSectionContentForm(obj=content)
    if form.validate_on_submit():
        form.populate_obj(content)
        try:
            db.session.commit()
            flash('Assistants Section content updated!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('admin_bp.edit_assistants_section_content'))
    return render_template('admin/edit_section_content_form.html', title="Edit Assistants Section Content", form=form)

# --- CreativitySectionContent ---
class CreativitySectionContentForm(FlaskForm):
    title = StringField('Section Title', validators=[DataRequired(), Length(max=100)])
    subtitle = TextAreaField('Section Subtitle', validators=[DataRequired(), Length(max=1000)])
    submit = SubmitField('Update Creativity Section Content')

@admin_bp.route('/edit_creativity_section_content', methods=['GET', 'POST'])
@login_required
def edit_creativity_section_content():
    content = CreativitySectionContent.query.first()
    if not content:
        flash('Error: CreativitySectionContent not found.', 'danger')
        return redirect(url_for('admin_bp.dashboard'))
    form = CreativitySectionContentForm(obj=content)
    if form.validate_on_submit():
        form.populate_obj(content)
        try:
            db.session.commit()
            flash('Creativity Section content updated!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('admin_bp.edit_creativity_section_content'))
    return render_template('admin/edit_section_content_form.html', title="Edit Creativity Section Content", form=form)

# --- LifestyleSectionContent ---
class LifestyleSectionContentForm(FlaskForm):
    title = StringField('Section Title', validators=[DataRequired(), Length(max=100)])
    subtitle = TextAreaField('Section Subtitle', validators=[DataRequired(), Length(max=1000)])
    submit = SubmitField('Update Lifestyle Section Content')

@admin_bp.route('/edit_lifestyle_section_content', methods=['GET', 'POST'])
@login_required
def edit_lifestyle_section_content():
    content = LifestyleSectionContent.query.first()
    if not content:
        flash('Error: LifestyleSectionContent not found.', 'danger')
        return redirect(url_for('admin_bp.dashboard'))
    form = LifestyleSectionContentForm(obj=content)
    if form.validate_on_submit():
        form.populate_obj(content)
        try:
            db.session.commit()
            flash('Lifestyle Section content updated!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('admin_bp.edit_lifestyle_section_content'))
    return render_template('admin/edit_section_content_form.html', title="Edit Lifestyle Section Content", form=form)

# --- InsightsSectionContent ---
class InsightsSectionContentForm(FlaskForm):
    title = StringField('Section Title', validators=[DataRequired(), Length(max=100)])
    subtitle = TextAreaField('Section Subtitle', validators=[DataRequired(), Length(max=1000)])
    chart1_title = StringField('Chart 1 Title', validators=[DataRequired(), Length(max=100)])
    chart2_title = StringField('Chart 2 Title', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Update Insights Section Content')

@admin_bp.route('/edit_insights_section_content', methods=['GET', 'POST'])
@login_required
def edit_insights_section_content():
    content = InsightsSectionContent.query.first()
    if not content:
        flash('Error: InsightsSectionContent not found.', 'danger')
        return redirect(url_for('admin_bp.dashboard'))
    form = InsightsSectionContentForm(obj=content)
    if form.validate_on_submit():
        form.populate_obj(content)
        try:
            db.session.commit()
            flash('Insights Section content updated!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('admin_bp.edit_insights_section_content'))
    return render_template('admin/edit_section_content_form.html', title="Edit Insights Section Content", form=form)

# --- ChallengesSectionContent ---
class ChallengesSectionContentForm(FlaskForm):
    title = StringField('Section Title', validators=[DataRequired(), Length(max=100)])
    subtitle = TextAreaField('Section Subtitle', validators=[DataRequired(), Length(max=1000)])
    accordion_section_title = StringField('Accordion Section Title (e.g., Key Challenges)', validators=[DataRequired(), Length(max=100)])
    future_trends_section_title = StringField('Future Trends Section Title', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Update Challenges Section Content')

@admin_bp.route('/edit_challenges_section_content', methods=['GET', 'POST'])
@login_required
def edit_challenges_section_content():
    content = ChallengesSectionContent.query.first()
    if not content:
        flash('Error: ChallengesSectionContent not found.', 'danger')
        return redirect(url_for('admin_bp.dashboard'))
    form = ChallengesSectionContentForm(obj=content)
    if form.validate_on_submit():
        form.populate_obj(content)
        try:
            db.session.commit()
            flash('Challenges Section content updated!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error: {str(e)}', 'danger')
        return redirect(url_for('admin_bp.edit_challenges_section_content'))
    return render_template('admin/edit_section_content_form.html', title="Edit Challenges Section Content", form=form)

class NavLinkForm(FlaskForm):
    text = StringField('Link Text', validators=[DataRequired(), Length(min=2, max=50)])
    href = StringField('Link URL/Href (e.g., #section or /page)', validators=[DataRequired(), Length(max=100)])
    order = IntegerField('Order', validators=[Optional()], default=0) # Optional, defaults to 0 if not provided
    submit = SubmitField('Save NavLink')

@admin_bp.route('/manage_nav_links')
@login_required
def manage_nav_links():
    links = NavLink.query.order_by(NavLink.order, NavLink.id).all()
    return render_template('admin/manage_nav_links.html', title="Manage Navigation Links", links=links)

@admin_bp.route('/add_nav_link', methods=['GET', 'POST'])
@login_required
def add_nav_link():
    form = NavLinkForm()
    if form.validate_on_submit():
        new_link = NavLink(
            text=form.text.data,
            href=form.href.data,
            order=form.order.data or 0 # Ensure order is not None
        )
        try:
            db.session.add(new_link)
            db.session.commit()
            flash('Navigation link added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding navigation link: {str(e)}', 'danger')
        return redirect(url_for('admin_bp.manage_nav_links'))
    return render_template('admin/nav_link_form.html', title="Add Navigation Link", form=form, form_action=url_for('admin_bp.add_nav_link'))

@admin_bp.route('/edit_nav_link/<int:link_id>', methods=['GET', 'POST'])
@login_required
def edit_nav_link(link_id):
    link = NavLink.query.get_or_404(link_id)
    form = NavLinkForm(obj=link)
    if form.validate_on_submit():
        link.text = form.text.data
        link.href = form.href.data
        link.order = form.order.data or 0
        try:
            db.session.commit()
            flash('Navigation link updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating navigation link: {str(e)}', 'danger')
        return redirect(url_for('admin_bp.manage_nav_links'))
    return render_template('admin/nav_link_form.html', title="Edit Navigation Link", form=form, form_action=url_for('admin_bp.edit_nav_link', link_id=link_id))

@admin_bp.route('/delete_nav_link/<int:link_id>', methods=['POST']) # Use POST for deletion
@login_required
def delete_nav_link(link_id):
    link = NavLink.query.get_or_404(link_id)
    try:
        db.session.delete(link)
        db.session.commit()
        flash('Navigation link deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting navigation link: {str(e)}', 'danger')
    return redirect(url_for('admin_bp.manage_nav_links'))

class AssistantCardForm(FlaskForm):
    title = StringField('Card Title', validators=[DataRequired(), Length(min=3, max=100)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=1000)])
    badge_text = StringField('Badge Text (e.g., "优点: 深度研究")', validators=[DataRequired(), Length(max=100)])
    # tab_category is fixed to 'chatbots' for this form/view logic.
    order = IntegerField('Order', validators=[Optional()], default=0)
    submit = SubmitField('Save Card')

@admin_bp.route('/manage_assistant_cards')
@login_required
def manage_assistant_cards():
    # Specifically for chatbot cards
    cards = AssistantCard.query.filter_by(tab_category='chatbots').order_by(AssistantCard.order, AssistantCard.id).all()
    return render_template('admin/manage_assistant_cards.html', title="Manage Chatbot Cards (AI Assistants)", cards=cards)

@admin_bp.route('/add_assistant_card', methods=['GET', 'POST'])
@login_required
def add_assistant_card():
    form = AssistantCardForm()
    if form.validate_on_submit():
        new_card = AssistantCard(
            title=form.title.data,
            description=form.description.data,
            badge_text=form.badge_text.data,
            order=form.order.data or 0,
            tab_category='chatbots' # Fixed for this management section
        )
        try:
            db.session.add(new_card)
            db.session.commit()
            flash('Chatbot card added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding card: {str(e)}', 'danger')
        return redirect(url_for('admin_bp.manage_assistant_cards'))
    return render_template('admin/assistant_card_form.html', title="Add Chatbot Card", form=form, form_action=url_for('admin_bp.add_assistant_card'))

@admin_bp.route('/edit_assistant_card/<int:card_id>', methods=['GET', 'POST'])
@login_required
def edit_assistant_card(card_id):
    card = AssistantCard.query.filter_by(id=card_id, tab_category='chatbots').first_or_404()
    form = AssistantCardForm(obj=card)
    if form.validate_on_submit():
        card.title = form.title.data
        card.description = form.description.data
        card.badge_text = form.badge_text.data
        card.order = form.order.data or 0
        try:
            db.session.commit()
            flash('Chatbot card updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating card: {str(e)}', 'danger')
        return redirect(url_for('admin_bp.manage_assistant_cards'))
    return render_template('admin/assistant_card_form.html', title="Edit Chatbot Card", form=form, form_action=url_for('admin_bp.edit_assistant_card', card_id=card_id))

@admin_bp.route('/delete_assistant_card/<int:card_id>', methods=['POST'])
@login_required
def delete_assistant_card(card_id):
    card = AssistantCard.query.filter_by(id=card_id, tab_category='chatbots').first_or_404()
    try:
        db.session.delete(card)
        db.session.commit()
        flash('Chatbot card deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting card: {str(e)}', 'danger')
    return redirect(url_for('admin_bp.manage_assistant_cards'))

class VoiceAssistantFeatureForm(FlaskForm):
    icon = StringField('Icon (Emoji, e.g., 🗣️)', validators=[DataRequired(), Length(max=10)])
    title = StringField('Feature Title', validators=[DataRequired(), Length(min=3, max=100)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=1000)])
    order = IntegerField('Order', validators=[Optional()], default=0)
    submit = SubmitField('Save Feature')

@admin_bp.route('/manage_voice_features')
@login_required
def manage_voice_features():
    features = VoiceAssistantFeature.query.order_by(VoiceAssistantFeature.order, VoiceAssistantFeature.id).all()
    return render_template('admin/manage_voice_features.html', title="Manage Voice Assistant Features", features=features)

@admin_bp.route('/add_voice_feature', methods=['GET', 'POST'])
@login_required
def add_voice_feature():
    form = VoiceAssistantFeatureForm()
    if form.validate_on_submit():
        new_feature = VoiceAssistantFeature(
            icon=form.icon.data,
            title=form.title.data,
            description=form.description.data,
            order=form.order.data or 0
        )
        try:
            db.session.add(new_feature)
            db.session.commit()
            flash('Voice assistant feature added successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding feature: {str(e)}', 'danger')
        return redirect(url_for('admin_bp.manage_voice_features'))
    return render_template('admin/voice_feature_form.html', title="Add Voice Assistant Feature", form=form, form_action=url_for('admin_bp.add_voice_feature'))

@admin_bp.route('/edit_voice_feature/<int:feature_id>', methods=['GET', 'POST'])
@login_required
def edit_voice_feature(feature_id):
    feature = VoiceAssistantFeature.query.get_or_404(feature_id)
    form = VoiceAssistantFeatureForm(obj=feature)
    if form.validate_on_submit():
        feature.icon = form.icon.data
        feature.title = form.title.data
        feature.description = form.description.data
        feature.order = form.order.data or 0
        try:
            db.session.commit()
            flash('Voice assistant feature updated successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating feature: {str(e)}', 'danger')
        return redirect(url_for('admin_bp.manage_voice_features'))
    return render_template('admin/voice_feature_form.html', title="Edit Voice Assistant Feature", form=form, form_action=url_for('admin_bp.edit_voice_feature', feature_id=feature_id))

@admin_bp.route('/delete_voice_feature/<int:feature_id>', methods=['POST'])
@login_required
def delete_voice_feature(feature_id):
    feature = VoiceAssistantFeature.query.get_or_404(feature_id)
    try:
        db.session.delete(feature)
        db.session.commit()
        flash('Voice assistant feature deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting feature: {str(e)}', 'danger')
    return redirect(url_for('admin_bp.manage_voice_features'))

# --- CreativityCard ---
class CreativityCardForm(FlaskForm):
    title = StringField('Card Title', validators=[DataRequired(), Length(max=100)])
    icon_emoji = StringField('Icon Emoji (e.g., 🎨)', validators=[Optional(), Length(max=10)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=1000)])
    ethical_warning = TextAreaField('Ethical Warning (Optional)', validators=[Optional(), Length(max=500)])
    order = IntegerField('Order', validators=[Optional()], default=0)
    submit = SubmitField('Save Creativity Card')

@admin_bp.route('/manage_creativity_cards')
@login_required
def manage_creativity_cards():
    cards = CreativityCard.query.order_by(CreativityCard.order, CreativityCard.id).all()
    return render_template('admin/manage_creativity_cards.html', title="Manage Creativity Cards", cards=cards)

@admin_bp.route('/add_creativity_card', methods=['GET', 'POST'])
@login_required
def add_creativity_card():
    form = CreativityCardForm()
    if form.validate_on_submit():
        new_card = CreativityCard(
            title=form.title.data, icon_emoji=form.icon_emoji.data,
            description=form.description.data, ethical_warning=form.ethical_warning.data,
            order=form.order.data or 0
        )
        db.session.add(new_card); db.session.commit()
        flash('Creativity card added!', 'success')
        return redirect(url_for('admin_bp.manage_creativity_cards'))
    return render_template('admin/creativity_card_form.html', title="Add Creativity Card", form=form, form_action=url_for('admin_bp.add_creativity_card'))

@admin_bp.route('/edit_creativity_card/<int:card_id>', methods=['GET', 'POST'])
@login_required
def edit_creativity_card(card_id):
    card = CreativityCard.query.get_or_404(card_id)
    form = CreativityCardForm(obj=card)
    if form.validate_on_submit():
        form.populate_obj(card)
        card.order = form.order.data or 0 # Ensure order has a value
        db.session.commit()
        flash('Creativity card updated!', 'success')
        return redirect(url_for('admin_bp.manage_creativity_cards'))
    return render_template('admin/creativity_card_form.html', title="Edit Creativity Card", form=form, form_action=url_for('admin_bp.edit_creativity_card', card_id=card_id))

@admin_bp.route('/delete_creativity_card/<int:card_id>', methods=['POST'])
@login_required
def delete_creativity_card(card_id):
    card = CreativityCard.query.get_or_404(card_id)
    db.session.delete(card); db.session.commit()
    flash('Creativity card deleted!', 'success')
    return redirect(url_for('admin_bp.manage_creativity_cards'))

# --- LifestyleCard ---
class LifestyleCardForm(FlaskForm):
    icon_emoji = StringField('Icon Emoji (e.g., 💼)', validators=[DataRequired(), Length(max=10)])
    title = StringField('Card Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=500)])
    order = IntegerField('Order', validators=[Optional()], default=0)
    submit = SubmitField('Save Lifestyle Card')

@admin_bp.route('/manage_lifestyle_cards')
@login_required
def manage_lifestyle_cards():
    cards = LifestyleCard.query.order_by(LifestyleCard.order, LifestyleCard.id).all()
    return render_template('admin/manage_lifestyle_cards.html', title="Manage Lifestyle Cards", cards=cards)

@admin_bp.route('/add_lifestyle_card', methods=['GET', 'POST'])
@login_required
def add_lifestyle_card():
    form = LifestyleCardForm()
    if form.validate_on_submit():
        new_card = LifestyleCard(
            icon_emoji=form.icon_emoji.data, title=form.title.data,
            description=form.description.data, order=form.order.data or 0
        )
        db.session.add(new_card); db.session.commit()
        flash('Lifestyle card added!', 'success')
        return redirect(url_for('admin_bp.manage_lifestyle_cards'))
    return render_template('admin/lifestyle_card_form.html', title="Add Lifestyle Card", form=form, form_action=url_for('admin_bp.add_lifestyle_card'))

@admin_bp.route('/edit_lifestyle_card/<int:card_id>', methods=['GET', 'POST'])
@login_required
def edit_lifestyle_card(card_id):
    card = LifestyleCard.query.get_or_404(card_id)
    form = LifestyleCardForm(obj=card)
    if form.validate_on_submit():
        form.populate_obj(card)
        card.order = form.order.data or 0
        db.session.commit()
        flash('Lifestyle card updated!', 'success')
        return redirect(url_for('admin_bp.manage_lifestyle_cards'))
    return render_template('admin/lifestyle_card_form.html', title="Edit Lifestyle Card", form=form, form_action=url_for('admin_bp.edit_lifestyle_card', card_id=card_id))

@admin_bp.route('/delete_lifestyle_card/<int:card_id>', methods=['POST'])
@login_required
def delete_lifestyle_card(card_id):
    card = LifestyleCard.query.get_or_404(card_id)
    db.session.delete(card); db.session.commit()
    flash('Lifestyle card deleted!', 'success')
    return redirect(url_for('admin_bp.manage_lifestyle_cards'))

# --- ChallengeItem (Accordion Items) ---
class ChallengeItemForm(FlaskForm):
    title = StringField('Item Title (can include emoji)', validators=[DataRequired(), Length(max=200)])
    content = TextAreaField('Content', validators=[DataRequired(), Length(max=2000)])
    order = IntegerField('Order', validators=[Optional()], default=0)
    submit = SubmitField('Save Challenge Item')

@admin_bp.route('/manage_challenge_items')
@login_required
def manage_challenge_items():
    items = ChallengeItem.query.order_by(ChallengeItem.order, ChallengeItem.id).all()
    return render_template('admin/manage_challenge_items.html', title="Manage Challenge Items (Accordion)", items=items)

@admin_bp.route('/add_challenge_item', methods=['GET', 'POST'])
@login_required
def add_challenge_item():
    form = ChallengeItemForm()
    if form.validate_on_submit():
        new_item = ChallengeItem(
            title=form.title.data, content=form.content.data, order=form.order.data or 0
        )
        db.session.add(new_item); db.session.commit()
        flash('Challenge item added!', 'success')
        return redirect(url_for('admin_bp.manage_challenge_items'))
    return render_template('admin/challenge_item_form.html', title="Add Challenge Item", form=form, form_action=url_for('admin_bp.add_challenge_item'))

@admin_bp.route('/edit_challenge_item/<int:item_id>', methods=['GET', 'POST'])
@login_required
def edit_challenge_item(item_id):
    item = ChallengeItem.query.get_or_404(item_id)
    form = ChallengeItemForm(obj=item)
    if form.validate_on_submit():
        form.populate_obj(item)
        item.order = form.order.data or 0
        db.session.commit()
        flash('Challenge item updated!', 'success')
        return redirect(url_for('admin_bp.manage_challenge_items'))
    return render_template('admin/challenge_item_form.html', title="Edit Challenge Item", form=form, form_action=url_for('admin_bp.edit_challenge_item', item_id=item_id))

@admin_bp.route('/delete_challenge_item/<int:item_id>', methods=['POST'])
@login_required
def delete_challenge_item(item_id):
    item = ChallengeItem.query.get_or_404(item_id)
    db.session.delete(item); db.session.commit()
    flash('Challenge item deleted!', 'success')
    return redirect(url_for('admin_bp.manage_challenge_items'))

# --- FutureTrend ---
class FutureTrendForm(FlaskForm):
    icon_emoji = StringField('Icon Emoji (e.g., 🤖)', validators=[DataRequired(), Length(max=10)])
    title = StringField('Trend Title', validators=[DataRequired(), Length(max=100)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=500)])
    order = IntegerField('Order', validators=[Optional()], default=0)
    submit = SubmitField('Save Future Trend')

@admin_bp.route('/manage_future_trends')
@login_required
def manage_future_trends():
    trends = FutureTrend.query.order_by(FutureTrend.order, FutureTrend.id).all()
    return render_template('admin/manage_future_trends.html', title="Manage Future Trends", trends=trends)

@admin_bp.route('/add_future_trend', methods=['GET', 'POST'])
@login_required
def add_future_trend():
    form = FutureTrendForm()
    if form.validate_on_submit():
        new_trend = FutureTrend(
            icon_emoji=form.icon_emoji.data, title=form.title.data,
            description=form.description.data, order=form.order.data or 0
        )
        db.session.add(new_trend); db.session.commit()
        flash('Future trend added!', 'success')
        return redirect(url_for('admin_bp.manage_future_trends'))
    return render_template('admin/future_trend_form.html', title="Add Future Trend", form=form, form_action=url_for('admin_bp.add_future_trend'))

@admin_bp.route('/edit_future_trend/<int:trend_id>', methods=['GET', 'POST'])
@login_required
def edit_future_trend(trend_id):
    trend = FutureTrend.query.get_or_404(trend_id)
    form = FutureTrendForm(obj=trend)
    if form.validate_on_submit():
        form.populate_obj(trend)
        trend.order = form.order.data or 0
        db.session.commit()
        flash('Future trend updated!', 'success')
        return redirect(url_for('admin_bp.manage_future_trends'))
    return render_template('admin/future_trend_form.html', title="Edit Future Trend", form=form, form_action=url_for('admin_bp.edit_future_trend', trend_id=trend_id))

@admin_bp.route('/delete_future_trend/<int:trend_id>', methods=['POST'])
@login_required
def delete_future_trend(trend_id):
    trend = FutureTrend.query.get_or_404(trend_id)
    db.session.delete(trend); db.session.commit()
    flash('Future trend deleted!', 'success')
    return redirect(url_for('admin_bp.manage_future_trends'))

# Register blueprint with the app (ensure this is done after app is defined)
# This line will be added separately by the modifier script:
# app.register_blueprint(admin_bp)

# Code to ensure SECRET_KEY is set and LoginManager is initialized with app
# This needs to be run in the context of app.py where 'app' is defined.
# The modifier script will take this block and place it appropriately after app init.
# For now, it's conceptually part of what admin_setup_changes.py provides.
# --- Begin App Context Block ---
# if not app.config.get('SECRET_KEY') or app.config.get('SECRET_KEY') == 'your_secret_key':
#     print("WARNING: Using a default or weak SECRET_KEY. Generating a new one for this session.")
#     app.config['SECRET_KEY'] = os.urandom(24).hex()
# login_manager.init_app(app)
# --- End App Context Block ---

@app.cli.command('init-db')
# def init_db_command():
#     create_db()
#     seed_initial_data()
#     print('Initialized the database and seeded initial data.')

@app.cli.command('init-db')
def init_db_command():
    with app.app_context():
        db.create_all()
    print('DB tables ensured.')
    seed_initial_data()
    print('Seeding invoked.')

@app.route('/')
def home():
    # Fetch all content from the database
    global_content = GlobalContent.query.first()
    nav_links = NavLink.query.order_by(NavLink.order).all()
    hero_section = HeroSection.query.first()
    assistants_section = AssistantsSectionContent.query.first()
    assistant_cards_chatbots = AssistantCard.query.filter_by(tab_category='chatbots').order_by(AssistantCard.order).all()
    voice_assistant_features = VoiceAssistantFeature.query.order_by(VoiceAssistantFeature.order).all()

    creativity_section = CreativitySectionContent.query.first()
    creativity_cards = CreativityCard.query.order_by(CreativityCard.order).all()

    lifestyle_section = LifestyleSectionContent.query.first()
    lifestyle_cards = LifestyleCard.query.order_by(LifestyleCard.order).all()

    insights_section = InsightsSectionContent.query.first()
    adoption_chart_db = ChartData.query.filter_by(chart_name='adoptionRateChart').first()
    demographics_chart_db = ChartData.query.filter_by(chart_name='demographicsChart').first()

    challenges_section = ChallengesSectionContent.query.first()
    challenge_items = ChallengeItem.query.order_by(ChallengeItem.order).all()
    future_trends = FutureTrend.query.order_by(FutureTrend.order).all()

    # Prepare chart data for JS. The template expects dicts with specific keys.
    adoption_chart_data = {
        'labels_json': adoption_chart_db.labels_json if adoption_chart_db else "[]",
        'data_json': adoption_chart_db.data_json if adoption_chart_db else "[]",
        'dataset_label': adoption_chart_db.dataset_label if adoption_chart_db else "Data"
    }
    demographics_chart_data = {
        'labels_json': demographics_chart_db.labels_json if demographics_chart_db else "[]",
        'data_json': demographics_chart_db.data_json if demographics_chart_db else "[]",
        'dataset_label': demographics_chart_db.dataset_label if demographics_chart_db else "Data"
    }

    return render_template(
        'index_template.html',
        title=global_content.page_title if global_content else 'AI Report CMS', # Default title if DB is empty
        global_content=global_content,
        nav_links=nav_links,
        hero=hero_section,
        assistants_section=assistants_section,
        assistant_cards_chatbots=assistant_cards_chatbots,
        voice_assistant_features=voice_assistant_features,
        creativity_section=creativity_section,
        creativity_cards=creativity_cards,
        lifestyle_section=lifestyle_section,
        lifestyle_cards=lifestyle_cards,
        insights_section=insights_section,
        adoption_chart=adoption_chart_data, # Pass the prepared dict
        demographics_chart=demographics_chart_data, # Pass the prepared dict
        challenges_section=challenges_section,
        challenge_items=challenge_items,
        future_trends=future_trends
    )


app.register_blueprint(admin_bp)

if __name__ == '__main__':
    app.run(debug=True)
