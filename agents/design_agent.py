# agents/design_agent.py
from agents.base_agent import BaseAgent

class DesignAgent(BaseAgent):
    def __init__(self, name="Design Agent"):
        super().__init__(name)

    def execute(self, task):
        print(f"{self.name}: Designing website based on task: {task}")
        topic = task.get("topic", "General Website")
        theme = task.get("theme", "basic")

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{topic.capitalize()}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header>
        <h1>{topic.capitalize()}</h1>
        <nav>
            <ul>
                <li><a href="#">Anasayfa</a></li>
                <li><a href="#">Hakkımızda</a></li>
                <li><a href="#">Ürünler</a></li>
                <li><a href="#">İletişim</a></li>
            </ul>
        </nav>
    </header>
    <main>
        <section id="content">
            <p>Bu, {topic.lower()} hakkında genel bir içerik alanıdır.</p>
        </section>
    </main>
    <footer>
        <p>&copy; {topic.capitalize()} 2025</p>
    </footer>
</body>
</html>"""

        css_content = """body {
    font-family: sans-serif;
    margin: 20px;
    background-color: #f4f4f4;
    color: #333;
}

header {
    background-color: #333;
    color: #fff;
    padding: 10px 0;
    text-align: center;
}

nav ul {
    padding: 0;
    list-style: none;
}

nav ul li {
    display: inline;
    margin: 0 15px;
}

nav a {
    color: #fff;
    text-decoration: none;
}

main {
    padding: 20px;
    background-color: #fff;
    border: 1px solid #ddd;
}

footer {
    text-align: center;
    padding: 10px 0;
    margin-top: 20px;
    background-color: #333;
    color: #fff;
}
"""

        return {"html": html_content, "css": css_content}