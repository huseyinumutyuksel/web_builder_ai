# agents/design_agent.py
from agents.base_agent import BaseAgent

class DesignAgent(BaseAgent):
    def __init__(self, name="Design Agent"):
        super().__init__(name)

    def execute(self, task): # İmza zaten task alıyordu, BaseAgent ile uyumlu
        print(f"{self.name}: Designing website based on task: {task}")
        topic = task.get("topic", "General Website")
        # theme = task.get("theme", "basic") # Tema şu anda HTML/CSS'e yansıtılmıyor, ileride kullanılabilir

        # HTML içeriğinde başlık ve h1 için daha genel yer tutucular veya ID'ler kullanılabilir
        # Şimdilik ManagerAgent'ın bunları doğru hedefleyebilmesi için mevcut yapıyı koruyoruz.
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
            <p>Bu, {topic.lower()} hakkında genel bir içerik alanıdır. Lütfen bekleyin, içerik yükleniyor...</p>
        </section>
        <section id="banner-image-section">
            </section>
    </main>
    <footer>
        <p>&copy; {topic.capitalize()} {task.get("year", 2025)}</p>
    </footer>
    </body>
</html>"""

        css_content = """body {
    font-family: sans-serif;
    margin: 0; /* Reset default margin */
    padding: 0; /* Reset default padding */
    background-color: #f4f4f4;
    color: #333;
    line-height: 1.6;
}

header {
    background-color: #333;
    color: #fff;
    padding: 1rem 0;
    text-align: center;
}

header h1 {
    margin: 0;
    font-size: 2.5rem;
}

nav ul {
    padding: 0;
    list-style: none;
    text-align: center;
}

nav ul li {
    display: inline;
    margin: 0 15px;
}

nav a {
    color: #fff;
    text-decoration: none;
    font-size: 1.1rem;
}

nav a:hover {
    text-decoration: underline;
}

main {
    padding: 20px;
    background-color: #fff;
    margin: 20px;
    border: 1px solid #ddd;
    border-radius: 5px;
}

#content h2 {
    color: #333;
}

#content img {
    max-width: 100%;
    height: auto;
    margin: 10px 0;
    border-radius: 4px;
}
#banner-image-section img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 20px auto;
    border: 1px solid #ddd;
    border-radius: 4px;
}


footer {
    text-align: center;
    padding: 20px 0;
    margin-top: 20px;
    background-color: #333;
    color: #fff;
}

/* Form Styles */
form {
    background: #f9f9f9;
    padding: 20px;
    border-radius: 5px;
    border: 1px solid #eee;
}

form div {
    margin-bottom: 15px;
}

form label {
    display: block;
    margin-bottom: 5px;
    font-weight: bold;
}

form input[type="text"],
form input[type="email"],
form textarea {
    width: calc(100% - 22px); /* Adjust for padding and border */
    padding: 10px;
    border: 1px solid #ddd;
    border-radius: 4px;
    box-sizing: border-box; /* Include padding and border in the element's total width and height */
}

form textarea {
    height: 100px;
    resize: vertical;
}

form button[type="submit"] {
    background-color: #5cb85c;
    color: white;
    padding: 10px 15px;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    font-size: 1rem;
}

form button[type="submit"]:hover {
    background-color: #4cae4c;
}

/* List Styles */
#content ul {
  list-style: disc;
  padding-left: 20px;
}
"""
        return {"html": html_content, "css": css_content}