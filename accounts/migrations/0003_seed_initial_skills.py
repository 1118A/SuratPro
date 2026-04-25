from django.db import migrations
from django.utils.text import slugify


INITIAL_SKILLS = [
    # Web & Frontend
    'HTML', 'CSS', 'JavaScript', 'TypeScript', 'React', 'Vue.js', 'Angular',
    'Next.js', 'Nuxt.js', 'Tailwind CSS', 'Bootstrap', 'SASS/SCSS',
    # Backend
    'Python', 'Django', 'Flask', 'FastAPI', 'Node.js', 'Express.js',
    'PHP', 'Laravel', 'Ruby on Rails', 'Java', 'Spring Boot',
    'Go', 'Rust', 'C#', '.NET', 'ASP.NET',
    # Mobile
    'React Native', 'Flutter', 'Swift', 'Kotlin', 'Android', 'iOS',
    # Databases
    'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'SQLite', 'Firebase',
    'Elasticsearch', 'GraphQL', 'REST API',
    # DevOps & Cloud
    'Docker', 'Kubernetes', 'AWS', 'Google Cloud', 'Azure',
    'CI/CD', 'Linux', 'Nginx', 'Terraform',
    # Design
    'UI/UX Design', 'Figma', 'Adobe XD', 'Photoshop', 'Illustrator',
    'Canva', 'Webflow', 'Responsive Design',
    # Data & AI
    'Machine Learning', 'Data Analysis', 'Data Science', 'TensorFlow',
    'PyTorch', 'Pandas', 'NumPy', 'SQL', 'Power BI', 'Tableau',
    # Content & Marketing
    'Copywriting', 'SEO', 'Content Writing', 'Social Media Marketing',
    'Email Marketing', 'WordPress', 'Shopify',
    # Other
    'Blockchain', 'Solidity', 'Web Scraping', 'Automation',
    'Cybersecurity', 'QA Testing', 'Selenium', 'Project Management',
]


def seed_skills(apps, schema_editor):
    Skill = apps.get_model('accounts', 'Skill')
    for name in INITIAL_SKILLS:
        slug = slugify(name)
        Skill.objects.get_or_create(slug=slug, defaults={'name': name})


def reverse_seed_skills(apps, schema_editor):
    # Do not delete skills on reverse — they may have been used
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_skill_portfolioitem_freelancerskill'),
    ]

    operations = [
        migrations.RunPython(seed_skills, reverse_seed_skills),
    ]
