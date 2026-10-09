import random
from datetime import datetime, timedelta
from app.database import SessionLocal, engine, Base
from app import models
from app.auth import get_password_hash
from app.recommender import recommender
from app.config import settings

# 120 curated realistic books across 12 genres
BOOKS_DATA = [
    # Science Fiction
    {
        "title": "Dune", "author": "Frank Herbert", "isbn": "978-0441013593", "genre": "Science Fiction",
        "year": 1965, "publisher": "Chilton Books", "shelf_location": "SF-01-A",
        "description": "Set on the desert planet Arrakis, Dune is the story of the boy Paul Atreides, heir to a noble family tasked with ruling an inhospitable world where the only thing of value is the spice melange.",
        "cover_image": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500&auto=format&fit=crop&q=80",
        "total_copies": 4
    },
    {
        "title": "Project Hail Mary", "author": "Andy Weir", "isbn": "978-0593135204", "genre": "Science Fiction",
        "year": 2021, "publisher": "Ballantine Books", "shelf_location": "SF-01-B",
        "description": "Ryland Grace is the sole survivor on a desperate, last-chance mission—and if he fails, humanity and the earth itself will perish.",
        "cover_image": "https://images.unsplash.com/photo-1618609377864-68609b857e90?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "Neuromancer", "author": "William Gibson", "isbn": "978-0441569595", "genre": "Science Fiction",
        "year": 1984, "publisher": "Ace Books", "shelf_location": "SF-01-C",
        "description": "Case was the sharpest data-thief in the matrix—until he crossed the wrong people and they crippled his nervous system with a wartime mycotoxin.",
        "cover_image": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "Foundation", "author": "Isaac Asimov", "isbn": "978-0553293357", "genre": "Science Fiction",
        "year": 1951, "publisher": "Gnome Press", "shelf_location": "SF-02-A",
        "description": "The story of Hari Seldon and psychohistory, predicting the fall of the Galactic Empire and establishing a foundation to preserve knowledge.",
        "cover_image": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "Snow Crash", "author": "Neal Stephenson", "isbn": "978-0553380958", "genre": "Science Fiction",
        "year": 1992, "publisher": "Bantam Books", "shelf_location": "SF-02-B",
        "description": "In reality, Hiro Protagonist delivers pizza for Uncle Enzo's CosoNostra Pizza Inc. But in the Metaverse he's a warrior prince chasing a new computer virus.",
        "cover_image": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=500&auto=format&fit=crop&q=80",
        "total_copies": 2
    },
    {
        "title": "The Three-Body Problem", "author": "Cixin Liu", "isbn": "978-0765382030", "genre": "Science Fiction",
        "year": 2008, "publisher": "Tor Books", "shelf_location": "SF-02-C",
        "description": "Set against the backdrop of China's Cultural Revolution, a secret military project sends signals into space to establish contact with aliens.",
        "cover_image": "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=500&auto=format&fit=crop&q=80",
        "total_copies": 4
    },
    {
        "title": "Hyperion", "author": "Dan Simmons", "isbn": "978-0553283686", "genre": "Science Fiction",
        "year": 1989, "publisher": "Doubleday", "shelf_location": "SF-03-A",
        "description": "On the world called Hyperion, beyond the reach of galactic law, waits a creature called the Shrike, worshiped by some, feared by all.",
        "cover_image": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=500&auto=format&fit=crop&q=80",
        "total_copies": 2
    },
    {
        "title": "Ender's Game", "author": "Orson Scott Card", "isbn": "978-0812550702", "genre": "Science Fiction",
        "year": 1985, "publisher": "Tor Books", "shelf_location": "SF-03-B",
        "description": "In order to develop a secure defense against a hostile alien race's next attack, government agencies breed child geniuses and train them as soldiers.",
        "cover_image": "https://images.unsplash.com/photo-1506703719100-a0f3a48c0f86?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "Solaris", "author": "Stanislaw Lem", "isbn": "978-0156027601", "genre": "Science Fiction",
        "year": 1961, "publisher": "Walker & Co", "shelf_location": "SF-03-C",
        "description": "A psychologist arrives on a space station orbiting the planet Solaris to study its sentient oceanic surface, only to encounter physical manifestations of his repressed memories.",
        "cover_image": "https://images.unsplash.com/photo-1462331940025-496dfbfc7564?w=500&auto=format&fit=crop&q=80",
        "total_copies": 2
    },
    {
        "title": "The Left Hand of Darkness", "author": "Ursula K. Le Guin", "isbn": "978-0441478125", "genre": "Science Fiction",
        "year": 1969, "publisher": "Ace Books", "shelf_location": "SF-04-A",
        "description": "A lone human envoy must navigate the complex icy world of Gethen, whose inhabitants can choose and change their gender.",
        "cover_image": "https://images.unsplash.com/photo-1484589065579-248aad0d8b13?w=500&auto=format&fit=crop&q=80",
        "total_copies": 2
    },

    # Mystery & Detective
    {
        "title": "The Hound of the Baskervilles", "author": "Arthur Conan Doyle", "isbn": "978-0140437867", "genre": "Mystery",
        "year": 1902, "publisher": "George Newnes", "shelf_location": "MYS-01-A",
        "description": "Sherlock Holmes and Dr. Watson investigate the curse of a spectral hound that haunts an aristocratic Devonshire family on Dartmoor.",
        "cover_image": "https://images.unsplash.com/photo-1589829085413-56de8ae18c73?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "And Then There Were None", "author": "Agatha Christie", "isbn": "978-0062073488", "genre": "Mystery",
        "year": 1939, "publisher": "Collins Crime Club", "shelf_location": "MYS-01-B",
        "description": "Ten strangers are lured to an isolated island mansion off the Devon coast. Once there, their eccentric host is missing, and one by one they are marked for murder.",
        "cover_image": "https://images.unsplash.com/photo-1543002588-bfa74002ed7e?w=500&auto=format&fit=crop&q=80",
        "total_copies": 4
    },
    {
        "title": "The Girl with the Dragon Tattoo", "author": "Stieg Larsson", "isbn": "978-0307949486", "genre": "Mystery",
        "year": 2005, "publisher": "Norstedts Forlag", "shelf_location": "MYS-01-C",
        "description": "Disgraced journalist Mikael Blomkvist and tattooed computer hacker Lisbeth Salander uncover dark family secrets on an island estate.",
        "cover_image": "https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "The Silent Patient", "author": "Alex Michaelides", "isbn": "978-1250301696", "genre": "Mystery",
        "year": 2019, "publisher": "Celadon Books", "shelf_location": "MYS-02-A",
        "description": "Alicia Berenson’s life is seemingly perfect. Then one evening she shoots her husband five times in the face and never speaks another word.",
        "cover_image": "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=500&auto=format&fit=crop&q=80",
        "total_copies": 4
    },
    {
        "title": "Gone Girl", "author": "Gillian Flynn", "isbn": "978-0307588371", "genre": "Mystery",
        "year": 2012, "publisher": "Crown Publishing", "shelf_location": "MYS-02-B",
        "description": "On their fifth wedding anniversary, Nick Dunne reports that his beautiful wife Amy has gone missing, but his evasive lies soon make him the prime suspect.",
        "cover_image": "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "Murder on the Orient Express", "author": "Agatha Christie", "isbn": "978-0062693662", "genre": "Mystery",
        "year": 1934, "publisher": "Collins Crime Club", "shelf_location": "MYS-02-C",
        "description": "Just after midnight, a snowdrift stops the Orient Express in its tracks. In the morning, an American tycoon lies dead in his compartment, stabbed a dozen times.",
        "cover_image": "https://images.unsplash.com/photo-1516979187457-637abb4f9353?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "The Da Vinci Code", "author": "Dan Brown", "isbn": "978-0307474278", "genre": "Mystery",
        "year": 2003, "publisher": "Doubleday", "shelf_location": "MYS-03-A",
        "description": "Symbologist Robert Langdon investigates a murder in the Louvre, discovering cryptic symbols and a centuries-old secret society conspiracy.",
        "cover_image": "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "In the Woods", "author": "Tana French", "isbn": "978-0143113492", "genre": "Mystery",
        "year": 2007, "publisher": "Viking Penguin", "shelf_location": "MYS-03-B",
        "description": "Detective Rob Ryan investigates the murder of a twelve-year-old girl in the same woods where his childhood friends disappeared decades earlier.",
        "cover_image": "https://images.unsplash.com/photo-1448375240586-882707db888b?w=500&auto=format&fit=crop&q=80",
        "total_copies": 2
    },
    {
        "title": "Big Little Lies", "author": "Liane Moriarty", "isbn": "978-0399587207", "genre": "Mystery",
        "year": 2014, "publisher": "Putnam", "shelf_location": "MYS-03-C",
        "description": "A brilliant take on ex-husbands and second wives, mothers and daughters, schoolyard scandal, and the dangerous little lies we tell ourselves to survive.",
        "cover_image": "https://images.unsplash.com/photo-1476275466078-4007374efbbe?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "Shutter Island", "author": "Dennis Lehane", "isbn": "978-0061898815", "genre": "Mystery",
        "year": 2003, "publisher": "William Morrow", "shelf_location": "MYS-04-A",
        "description": "US Marshal Teddy Daniels arrives at Ashecliffe Hospital on Shutter Island to investigate the disappearance of a murderess from a locked room.",
        "cover_image": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=500&auto=format&fit=crop&q=80",
        "total_copies": 2
    },

    # Technology & Programming
    {
        "title": "Clean Code", "author": "Robert C. Martin", "isbn": "978-0132350884", "genre": "Technology",
        "year": 2008, "publisher": "Prentice Hall", "shelf_location": "TECH-01-A",
        "description": "A handbook of agile software craftsmanship teaching principles, patterns, and practices of writing clean, maintainable, readable code.",
        "cover_image": "https://images.unsplash.com/photo-1517694712202-14dd9538aa97?w=500&auto=format&fit=crop&q=80",
        "total_copies": 4
    },
    {
        "title": "Designing Data-Intensive Applications", "author": "Martin Kleppmann", "isbn": "978-1449373320", "genre": "Technology",
        "year": 2017, "publisher": "O'Reilly Media", "shelf_location": "TECH-01-B",
        "description": "The big ideas behind reliable, scalable, and maintainable systems. Explores data models, storage engines, distributed consensus, and streaming.",
        "cover_image": "https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=500&auto=format&fit=crop&q=80",
        "total_copies": 4
    },
    {
        "title": "The Pragmatic Programmer", "author": "David Thomas, Andrew Hunt", "isbn": "978-0135957059", "genre": "Technology",
        "year": 2019, "publisher": "Addison-Wesley", "shelf_location": "TECH-01-C",
        "description": "From journey to master: core engineering wisdom spanning software craftsmanship, modular architectures, testing discipline, and continuous learning.",
        "cover_image": "https://images.unsplash.com/photo-1531403009284-440f080d1e12?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "Introduction to Algorithms", "author": "Thomas H. Cormen", "isbn": "978-0262046305", "genre": "Technology",
        "year": 2022, "publisher": "MIT Press", "shelf_location": "TECH-02-A",
        "description": "The legendary CLRS comprehensive textbook on modern algorithms, data structures, dynamic programming, graph theory, and computational complexity.",
        "cover_image": "https://images.unsplash.com/photo-1516116211227-bbc868a24c51?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "Grokking Algorithms", "author": "Aditya Bhargava", "isbn": "978-1617292231", "genre": "Technology",
        "year": 2016, "publisher": "Manning Publications", "shelf_location": "TECH-02-B",
        "description": "A fully illustrated, friendly guide that teaches you how to apply common algorithms to practical software problems with Python examples.",
        "cover_image": "https://images.unsplash.com/photo-1515879218367-8466d910aaa4?w=500&auto=format&fit=crop&q=80",
        "total_copies": 4
    },
    {
        "title": "Fluent Python", "author": "Luciano Ramalho", "isbn": "978-1492056355", "genre": "Technology",
        "year": 2022, "publisher": "O'Reilly Media", "shelf_location": "TECH-02-C",
        "description": "Clear, idiomatic Python guide detailing decorators, generators, metaclasses, asyncio, type hints, and modern Python 3 features.",
        "cover_image": "https://images.unsplash.com/photo-1526379095098-d400fd0bf935?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "Deep Learning with Python", "author": "Francois Chollet", "isbn": "978-1617296864", "genre": "Technology",
        "year": 2021, "publisher": "Manning Publications", "shelf_location": "TECH-03-A",
        "description": "Introduces the field of neural networks and deep learning using Python and the Keras library, written by the creator of Keras.",
        "cover_image": "https://images.unsplash.com/photo-1555949963-aa79dcee981c?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "Structure and Interpretation of Computer Programs", "author": "Harold Abelson, Gerald Jay Sussman", "isbn": "978-0262510875", "genre": "Technology",
        "year": 1996, "publisher": "MIT Press", "shelf_location": "TECH-03-B",
        "description": "The seminal wizard book exploring computational abstractions, interpreters, procedural abstraction, and functional programming.",
        "cover_image": "https://images.unsplash.com/photo-1504639725590-34d0984388bd?w=500&auto=format&fit=crop&q=80",
        "total_copies": 2
    },
    {
        "title": "Refactoring", "author": "Martin Fowler", "isbn": "978-0134757599", "genre": "Technology",
        "year": 2018, "publisher": "Addison-Wesley", "shelf_location": "TECH-03-C",
        "description": "Improving the design of existing code through disciplined, cataloged transformations without changing its observable external behavior.",
        "cover_image": "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "You Don't Know JS Yet", "author": "Kyle Simpson", "isbn": "978-1934356708", "genre": "Technology",
        "year": 2020, "publisher": "Getify Solutions", "shelf_location": "TECH-04-A",
        "description": "Deep dive into JavaScript core mechanics, scope, closures, prototypes, asynchronous events, and the type system.",
        "cover_image": "https://images.unsplash.com/photo-1579468118864-1b9ea3c0db4a?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },

    # Fantasy
    {
        "title": "The Hobbit", "author": "J.R.R. Tolkien", "isbn": "978-0547928227", "genre": "Fantasy",
        "year": 1937, "publisher": "George Allen & Unwin", "shelf_location": "FAN-01-A",
        "description": "Bilbo Baggins is a hobbit who enjoys a comfortable, unambitious life, until Gandalf the wizard and a company of dwarves arrive to enlist him on a quest for dragon gold.",
        "cover_image": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=500&auto=format&fit=crop&q=80",
        "total_copies": 4
    },
    {
        "title": "The Name of the Wind", "author": "Patrick Rothfuss", "isbn": "978-0756404741", "genre": "Fantasy",
        "year": 2007, "publisher": "DAW Books", "shelf_location": "FAN-01-B",
        "description": "The tale of Kvothe, from his childhood in a troupe of traveling players to his years at the University learning magic and his transformation into a living legend.",
        "cover_image": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "The Way of Kings", "author": "Brandon Sanderson", "isbn": "978-0765365279", "genre": "Fantasy",
        "year": 2010, "publisher": "Tor Books", "shelf_location": "FAN-01-C",
        "description": "Roshar is a world of stone and storms. War rages on the Shattered Plains as ancient weapons of mystical power and lost Radiants begin to awaken.",
        "cover_image": "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=500&auto=format&fit=crop&q=80",
        "total_copies": 4
    },
    {
        "title": "A Game of Thrones", "author": "George R.R. Martin", "isbn": "978-0553103540", "genre": "Fantasy",
        "year": 1996, "publisher": "Bantam Spectra", "shelf_location": "FAN-02-A",
        "description": "In a land where summers can span decades and winters a lifetime, noble families conspire for the Iron Throne of Westeros while an ancient threat stirs in the far north.",
        "cover_image": "https://images.unsplash.com/photo-1514533450685-4493e01d1fdc?w=500&auto=format&fit=crop&q=80",
        "total_copies": 4
    },
    {
        "title": "The Fellowship of the Ring", "author": "J.R.R. Tolkien", "isbn": "978-0547928210", "genre": "Fantasy",
        "year": 1954, "publisher": "George Allen & Unwin", "shelf_location": "FAN-02-B",
        "description": "The first volume of The Lord of the Rings follows Frodo Baggins as he inherits the One Ring and begins the peril-fraught pilgrimage to Mount Doom.",
        "cover_image": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "Mistborn: The Final Empire", "author": "Brandon Sanderson", "isbn": "978-0765350381", "genre": "Fantasy",
        "year": 2006, "publisher": "Tor Books", "shelf_location": "FAN-02-C",
        "description": "For a thousand years the ash fell and no flowers bloomed. An allomancer thief gathers an elite crew to pull off the ultimate heist: overthrowing the immortal Lord Ruler.",
        "cover_image": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "Good Omens", "author": "Neil Gaiman, Terry Pratchett", "isbn": "978-0060853983", "genre": "Fantasy",
        "year": 1990, "publisher": "Gollancz", "shelf_location": "FAN-03-A",
        "description": "An angel and a demon who have grown quite fond of their comfortable lives in England must join forces to prevent the upcoming apocalypse.",
        "cover_image": "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "American Gods", "author": "Neil Gaiman", "isbn": "978-0060558123", "genre": "Fantasy",
        "year": 2001, "publisher": "William Morrow", "shelf_location": "FAN-03-B",
        "description": "Shadow Moon is released from prison and hired as a bodyguard by the enigmatic Mr. Wednesday, who is rallying mythological gods against new modern deities.",
        "cover_image": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=500&auto=format&fit=crop&q=80",
        "total_copies": 2
    },
    {
        "title": "Circe", "author": "Madeline Miller", "isbn": "978-0316556347", "genre": "Fantasy",
        "year": 2018, "publisher": "Little, Brown and Company", "shelf_location": "FAN-03-C",
        "description": "In the house of Helios, god of the sun, a daughter is born who possesses the power of witchcraft. Exiled to a deserted island, she tames wild beasts and defies gods.",
        "cover_image": "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "The Priory of the Orange Tree", "author": "Samantha Shannon", "isbn": "978-1635570298", "genre": "Fantasy",
        "year": 2019, "publisher": "Bloomsbury Publishing", "shelf_location": "FAN-04-A",
        "description": "An epic, diverse high fantasy tale of an unwed queen, a divided world of dragon riders and mages, and an ancient nameless evil threatening to rise.",
        "cover_image": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=500&auto=format&fit=crop&q=80",
        "total_copies": 2
    },

    # Non-Fiction & Science
    {
        "title": "Sapiens: A Brief History of Humankind", "author": "Yuval Noah Harari", "isbn": "978-0062316097", "genre": "Non-Fiction",
        "year": 2014, "publisher": "Harper", "shelf_location": "NF-01-A",
        "description": "Explores how an insignificant ape became the ruler of planet Earth through the cognitive, agricultural, and scientific revolutions.",
        "cover_image": "https://images.unsplash.com/photo-1457369804613-52c61a468e7d?w=500&auto=format&fit=crop&q=80",
        "total_copies": 4
    },
    {
        "title": "Thinking, Fast and Slow", "author": "Daniel Kahneman", "isbn": "978-0374533557", "genre": "Non-Fiction",
        "year": 2011, "publisher": "Farrar, Straus and Giroux", "shelf_location": "NF-01-B",
        "description": "Nobel laureate Daniel Kahneman explains the two systems that drive the way we think: System 1 is fast, intuitive, and emotional; System 2 is slower and more deliberate.",
        "cover_image": "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "Atomic Habits", "author": "James Clear", "isbn": "978-0735211292", "genre": "Non-Fiction",
        "year": 2018, "publisher": "Avery", "shelf_location": "NF-01-C",
        "description": "An easy and proven way to build good habits and break bad ones. Small changes lead to remarkable, compounding results over time.",
        "cover_image": "https://images.unsplash.com/photo-1544717305-2782549b5136?w=500&auto=format&fit=crop&q=80",
        "total_copies": 5
    },
    {
        "title": "A Brief History of Time", "author": "Stephen Hawking", "isbn": "978-0553380163", "genre": "Non-Fiction",
        "year": 1988, "publisher": "Bantam Books", "shelf_location": "NF-02-A",
        "description": "From the big bang to black holes, theoretical physicist Stephen Hawking explores the frontiers of time and space in clear, accessible prose.",
        "cover_image": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "Cosmos", "author": "Carl Sagan", "isbn": "978-0345331359", "genre": "Non-Fiction",
        "year": 1980, "publisher": "Random House", "shelf_location": "NF-02-B",
        "description": "Carl Sagan traces fifteen billion years of cosmic evolution, exploring the science, philosophy, and history of our search for our place in the universe.",
        "cover_image": "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "The Selfish Gene", "author": "Richard Dawkins", "isbn": "978-0199291151", "genre": "Non-Fiction",
        "year": 1976, "publisher": "Oxford University Press", "shelf_location": "NF-02-C",
        "description": "A classic work that reshaped biological thinking by arguing that natural selection acts on the gene level rather than the organism or group.",
        "cover_image": "https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=500&auto=format&fit=crop&q=80",
        "total_copies": 2
    },
    {
        "title": "Guns, Germs, and Steel", "author": "Jared Diamond", "isbn": "978-0393354324", "genre": "Non-Fiction",
        "year": 1997, "publisher": "W. W. Norton", "shelf_location": "NF-03-A",
        "description": "A transdisciplinary study of human societies explaining how geographic and environmental factors shaped modern civilization over 13,000 years.",
        "cover_image": "https://images.unsplash.com/photo-1461360370896-922624d12aa1?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "The Immortal Life of Henrietta Lacks", "author": "Rebecca Skloot", "isbn": "978-1400052189", "genre": "Non-Fiction",
        "year": 2010, "publisher": "Crown Publishing", "shelf_location": "NF-03-B",
        "description": "The gripping story of the woman whose cancer cells—taken without her knowledge in 1951—became an invaluable tool in medical history.",
        "cover_image": "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "Astrophysics for People in a Hurry", "author": "Neil deGrasse Tyson", "isbn": "978-0393609394", "genre": "Non-Fiction",
        "year": 2017, "publisher": "W. W. Norton", "shelf_location": "NF-03-C",
        "description": "What is the nature of space and time? How do we fit within the cosmos? An essential, mind-expanding guide to cosmic physics.",
        "cover_image": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "The Gene: An Intimate History", "author": "Siddhartha Mukherjee", "isbn": "978-1476733524", "genre": "Non-Fiction",
        "year": 2016, "publisher": "Scribner", "shelf_location": "NF-04-A",
        "description": "Pulitzer Prize winner Siddhartha Mukherjee tells the story of the gene—the fundamental unit of heredity and one of the most powerful ideas in science.",
        "cover_image": "https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=500&auto=format&fit=crop&q=80",
        "total_copies": 2
    },

    # History & Biography
    {
        "title": "Steve Jobs", "author": "Walter Isaacson", "isbn": "978-1451648539", "genre": "Biography",
        "year": 2011, "publisher": "Simon & Schuster", "shelf_location": "BIO-01-A",
        "description": "Based on more than forty interviews with Jobs conducted over two years, this is the definitive biography of the creative entrepreneur who revolutionized six industries.",
        "cover_image": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=500&auto=format&fit=crop&q=80",
        "total_copies": 4
    },
    {
        "title": "Educated", "author": "Tara Westover", "isbn": "978-0399590504", "genre": "Biography",
        "year": 2018, "publisher": "Random House", "shelf_location": "BIO-01-B",
        "description": "Born to survivalists in the mountains of Idaho, Tara Westover stepped into a classroom for the first time at age seventeen and eventually earned a PhD from Cambridge.",
        "cover_image": "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=500&auto=format&fit=crop&q=80",
        "total_copies": 4
    },
    {
        "title": "Shoe Dog: A Memoir by the Creator of Nike", "author": "Phil Knight", "isbn": "978-1501135927", "genre": "Biography",
        "year": 2016, "publisher": "Scribner", "shelf_location": "BIO-01-C",
        "description": "Nike founder and board chairman Phil Knight shares the inside story of the company’s early days as an intrepid start-up and its evolution into one of the world's most iconic brands.",
        "cover_image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "The Diary of a Young Girl", "author": "Anne Frank", "isbn": "978-0553296983", "genre": "Biography",
        "year": 1947, "publisher": "Contact Publishing", "shelf_location": "BIO-02-A",
        "description": "Discovered in the attic in which she spent the last years of her life, Anne Frank’s remarkable diary has become a world classic and testament to the human spirit.",
        "cover_image": "https://images.unsplash.com/photo-1457369804613-52c61a468e7d?w=500&auto=format&fit=crop&q=80",
        "total_copies": 4
    },
    {
        "title": "Born a Crime", "author": "Trevor Noah", "isbn": "978-0399588198", "genre": "Biography",
        "year": 2016, "publisher": "Spiegel & Grau", "shelf_location": "BIO-02-B",
        "description": "Stories from a South African childhood: Trevor Noah’s unlikely path from apartheid to the desk of The Daily Show, told with wit, resilience, and heart.",
        "cover_image": "https://images.unsplash.com/photo-1544717305-2782549b5136?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "Alexander Hamilton", "author": "Ron Chernow", "isbn": "978-0143034758", "genre": "Biography",
        "year": 2004, "publisher": "Penguin Books", "shelf_location": "BIO-02-C",
        "description": "The Pulitzer Prize-winning biographer's account of the passionate, visionary founding father who galvanized the financial architecture of the United States.",
        "cover_image": "https://images.unsplash.com/photo-1461360370896-922624d12aa1?w=500&auto=format&fit=crop&q=80",
        "total_copies": 2
    },
    {
        "title": "Leonardo da Vinci", "author": "Walter Isaacson", "isbn": "978-1501139161", "genre": "Biography",
        "year": 2017, "publisher": "Simon & Schuster", "shelf_location": "BIO-03-A",
        "description": "A vivid journey through the life of history’s most creative genius, weaving together his art, anatomy, engineering, and boundless curiosity.",
        "cover_image": "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "Team of Rivals", "author": "Doris Kearns Goodwin", "isbn": "978-0743270755", "genre": "Biography",
        "year": 2005, "publisher": "Simon & Schuster", "shelf_location": "BIO-03-B",
        "description": "The political genius of Abraham Lincoln, showing how he reconciled disparate rivals into his cabinet to preserve the American Union.",
        "cover_image": "https://images.unsplash.com/photo-1461360370896-922624d12aa1?w=500&auto=format&fit=crop&q=80",
        "total_copies": 2
    },
    {
        "title": "The Wright Brothers", "author": "David McCullough", "isbn": "978-1476728759", "genre": "Biography",
        "year": 2015, "publisher": "Simon & Schuster", "shelf_location": "BIO-03-C",
        "description": "Two-time Pulitzer Prize winner David McCullough tells the dramatic story of the courageous brothers who taught the world how to fly.",
        "cover_image": "https://images.unsplash.com/photo-1519074069444-1ba4e4eefec2?w=500&auto=format&fit=crop&q=80",
        "total_copies": 2
    },
    {
        "title": "Churchill: A Life", "author": "Martin Gilbert", "isbn": "978-0805023961", "genre": "Biography",
        "year": 1991, "publisher": "Henry Holt and Co", "shelf_location": "BIO-04-A",
        "description": "The authoritative single-volume life of Britain's wartime leader Winston Churchill, chronicling courage, eloquence, and global leadership.",
        "cover_image": "https://images.unsplash.com/photo-1461360370896-922624d12aa1?w=500&auto=format&fit=crop&q=80",
        "total_copies": 2
    },

    # Literary Fiction
    {
        "title": "1984", "author": "George Orwell", "isbn": "978-0451524935", "genre": "Fiction",
        "year": 1949, "publisher": "Secker & Warburg", "shelf_location": "FIC-01-A",
        "description": "Winston Smith struggles against the totalitarian regime of Big Brother in a society that enforces total surveillance, historical revisionism, and doublethink.",
        "cover_image": "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=500&auto=format&fit=crop&q=80",
        "total_copies": 4
    },
    {
        "title": "To Kill a Mockingbird", "author": "Harper Lee", "isbn": "978-0060935467", "genre": "Fiction",
        "year": 1960, "publisher": "J. B. Lippincott & Co.", "shelf_location": "FIC-01-B",
        "description": "Through the young eyes of Scout Finch in Alabama, Atticus Finch risks his community standing to defend a Black man falsely accused of a horrific crime.",
        "cover_image": "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=500&auto=format&fit=crop&q=80",
        "total_copies": 4
    },
    {
        "title": "The Great Gatsby", "author": "F. Scott Fitzgerald", "isbn": "978-0743273565", "genre": "Fiction",
        "year": 1925, "publisher": "Charles Scribner's Sons", "shelf_location": "FIC-01-C",
        "description": "The tragic romance of enigmatic millionaire Jay Gatsby and his obsessive yearning for Daisy Buchanan amid Jazz Age prosperity and disillusionment.",
        "cover_image": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "Crime and Punishment", "author": "Fyodor Dostoevsky", "isbn": "978-0140449136", "genre": "Fiction",
        "year": 1866, "publisher": "The Russian Messenger", "shelf_location": "FIC-02-A",
        "description": "An impoverished ex-student in St. Petersburg plans to kill an unscrupulous pawnbroker to test his theory of superior human rights.",
        "cover_image": "https://images.unsplash.com/photo-1457369804613-52c61a468e7d?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "One Hundred Years of Solitude", "author": "Gabriel Garcia Marquez", "isbn": "978-0060883287", "genre": "Fiction",
        "year": 1967, "publisher": "Harper & Row", "shelf_location": "FIC-02-B",
        "description": "The multi-generational story of the Buendia family in the mythical town of Macondo, blending magical realism and Latin American history.",
        "cover_image": "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "Brave New World", "author": "Aldous Huxley", "isbn": "978-0060850524", "genre": "Fiction",
        "year": 1932, "publisher": "Chatto & Windus", "shelf_location": "FIC-02-C",
        "description": "In a genetically engineered future of synthetic contentment and consumption, Bernard Marx and John the Savage challenge the illusion of happiness.",
        "cover_image": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "The Catcher in the Rye", "author": "J.D. Salinger", "isbn": "978-0316769488", "genre": "Fiction",
        "year": 1951, "publisher": "Little, Brown and Company", "shelf_location": "FIC-03-A",
        "description": "Holden Caulfield recounts two days wandering New York City after being expelled from his prep school, grappling with phoniness and innocence.",
        "cover_image": "https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "Beloved", "author": "Toni Morrison", "isbn": "978-1400033416", "genre": "Fiction",
        "year": 1987, "publisher": "Alfred A. Knopf", "shelf_location": "FIC-03-B",
        "description": "Set after the American Civil War, Sethe is haunted by the ghost of her baby daughter whom she killed to save from slavery.",
        "cover_image": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500&auto=format&fit=crop&q=80",
        "total_copies": 2
    },
    {
        "title": "Midnight's Children", "author": "Salman Rushdie", "isbn": "978-0812976533", "genre": "Fiction",
        "year": 1981, "publisher": "Jonathan Cape", "shelf_location": "FIC-03-C",
        "description": "Saleem Sinai is born at the exact stroke of midnight as India gains independence, blessed with telepathic powers linking him to all children born in that hour.",
        "cover_image": "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=500&auto=format&fit=crop&q=80",
        "total_copies": 2
    },
    {
        "title": "Pride and Prejudice", "author": "Jane Austen", "isbn": "978-0141439518", "genre": "Fiction",
        "year": 1813, "publisher": "T. Egerton", "shelf_location": "FIC-04-A",
        "description": "The witty battle of manners, marriage, and pride between independent Elizabeth Bennet and aristocratic Mr. Darcy in Regency England.",
        "cover_image": "https://images.unsplash.com/photo-1544717305-2782549b5136?w=500&auto=format&fit=crop&q=80",
        "total_copies": 4
    },

    # Philosophy
    {
        "title": "Meditations", "author": "Marcus Aurelius", "isbn": "978-0812968255", "genre": "Philosophy",
        "year": 180, "publisher": "Penguin Classics", "shelf_location": "PHIL-01-A",
        "description": "Private journal reflections of the Roman Emperor Marcus Aurelius on Stoic duty, calmness of mind, and virtue amidst mortal trials.",
        "cover_image": "https://images.unsplash.com/photo-1457369804613-52c61a468e7d?w=500&auto=format&fit=crop&q=80",
        "total_copies": 4
    },
    {
        "title": "Man's Search for Meaning", "author": "Viktor E. Frankl", "isbn": "978-0807014295", "genre": "Philosophy",
        "year": 1946, "publisher": "Beacon Press", "shelf_location": "PHIL-01-B",
        "description": "Psychiatrist Viktor Frankl’s memoir of surviving Auschwitz and discovering that spiritual freedom and personal meaning sustain human existence.",
        "cover_image": "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=500&auto=format&fit=crop&q=80",
        "total_copies": 4
    },
    {
        "title": "The Republic", "author": "Plato", "isbn": "978-0140455113", "genre": "Philosophy",
        "year": -375, "publisher": "Penguin Books", "shelf_location": "PHIL-01-C",
        "description": "Socratic dialogues examining justice, the ideal city-state, the Philosopher King, and the famous Allegory of the Cave.",
        "cover_image": "https://images.unsplash.com/photo-1461360370896-922624d12aa1?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "Beyond Good and Evil", "author": "Friedrich Nietzsche", "isbn": "978-0140449235", "genre": "Philosophy",
        "year": 1886, "publisher": "C. G. Naumann", "shelf_location": "PHIL-02-A",
        "description": "Nietzsche dismantles traditional Western morality, exposing dogmatism and proposing the will to power and intellectual independence.",
        "cover_image": "https://images.unsplash.com/photo-1457369804613-52c61a468e7d?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "Letters from a Stoic", "author": "Seneca", "isbn": "978-0140442106", "genre": "Philosophy",
        "year": 65, "publisher": "Penguin Classics", "shelf_location": "PHIL-02-B",
        "description": "Epistles from Lucius Annaeus Seneca offering practical advice on grief, friendship, wealth, and living a tranquil Stoic life.",
        "cover_image": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "The Myth of Sisyphus", "author": "Albert Camus", "isbn": "978-0679733737", "genre": "Philosophy",
        "year": 1942, "publisher": "Gallimard", "shelf_location": "PHIL-02-C",
        "description": "Camus investigates the absurd: the tension between humanity's search for inherent meaning and the silent, indifferent universe.",
        "cover_image": "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "Justice: What's the Right Thing to Do?", "author": "Michael J. Sandel", "isbn": "978-0374532505", "genre": "Philosophy",
        "year": 2009, "publisher": "Farrar, Straus and Giroux", "shelf_location": "PHIL-03-A",
        "description": "Harvard professor Michael Sandel tackles moral quandaries, utilitarianism, Kantian ethics, and civic virtue in modern society.",
        "cover_image": "https://images.unsplash.com/photo-1589829085413-56de8ae18c73?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "Nicomachean Ethics", "author": "Aristotle", "isbn": "978-0199213610", "genre": "Philosophy",
        "year": -350, "publisher": "Oxford World's Classics", "shelf_location": "PHIL-03-B",
        "description": "Aristotle's exploration of eudaimonia (human flourishing), the Golden Mean, and the cultivation of intellectual and moral virtues.",
        "cover_image": "https://images.unsplash.com/photo-1461360370896-922624d12aa1?w=500&auto=format&fit=crop&q=80",
        "total_copies": 2
    },
    {
        "title": "Being and Time", "author": "Martin Heidegger", "isbn": "978-0631197706", "genre": "Philosophy",
        "year": 1927, "publisher": "Max Niemeyer Verlag", "shelf_location": "PHIL-03-C",
        "description": "An inquiry into the meaning of Being through the lens of human existence (Dasein), temporality, anxiety, and authenticity.",
        "cover_image": "https://images.unsplash.com/photo-1457369804613-52c61a468e7d?w=500&auto=format&fit=crop&q=80",
        "total_copies": 2
    },
    {
        "title": "Critique of Pure Reason", "author": "Immanuel Kant", "isbn": "978-0521657297", "genre": "Philosophy",
        "year": 1781, "publisher": "Johann Friedrich Hartknoch", "shelf_location": "PHIL-04-A",
        "description": "Kant’s monumental work synthesizing rationalism and empiricism, examining the limits and scope of human knowledge and synthetic a priori judgments.",
        "cover_image": "https://images.unsplash.com/photo-1461360370896-922624d12aa1?w=500&auto=format&fit=crop&q=80",
        "total_copies": 2
    },

    # Thriller & Suspense
    {
        "title": "The Silence of the Lambs", "author": "Thomas Harris", "isbn": "978-0312924584", "genre": "Thriller",
        "year": 1988, "publisher": "St. Martin's Press", "shelf_location": "THR-01-A",
        "description": "FBI trainee Clarice Starling interviews imprisoned psychiatrist and cannibal Dr. Hannibal Lecter to catch a serial killer named Buffalo Bill.",
        "cover_image": "https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "Dark Matter", "author": "Blake Crouch", "isbn": "978-1101904244", "genre": "Thriller",
        "year": 2016, "publisher": "Crown Publishing", "shelf_location": "THR-01-B",
        "description": "A college physics professor is abducted and wakes up in a laboratory where his invention of a multiverse gateway has succeeded—but his wife and son are gone.",
        "cover_image": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=500&auto=format&fit=crop&q=80",
        "total_copies": 4
    },
    {
        "title": "The Bourne Identity", "author": "Robert Ludlum", "isbn": "978-0553593549", "genre": "Thriller",
        "year": 1980, "publisher": "Richard Marek Publishers", "shelf_location": "THR-01-C",
        "description": "A man pulled from the Mediterranean with amnesia discovers microfilm embedded in his hip and lethal combat skills he cannot remember learning.",
        "cover_image": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "Sharp Objects", "author": "Gillian Flynn", "isbn": "978-0307341556", "genre": "Thriller",
        "year": 2006, "publisher": "Shaye Areheart Books", "shelf_location": "THR-02-A",
        "description": "Fresh from a brief stay at a psych hospital, journalist Camille Preaker faces a troubling assignment: return to her tiny hometown to cover unsolved murders.",
        "cover_image": "https://images.unsplash.com/photo-1543002588-bfa74002ed7e?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "Red Dragon", "author": "Thomas Harris", "isbn": "978-0425228227", "genre": "Thriller",
        "year": 1981, "publisher": "G. P. Putnam's Sons", "shelf_location": "THR-02-B",
        "description": "Former FBI profiler Will Graham comes out of retirement to track a ruthless killer who strikes during full moons.",
        "cover_image": "https://images.unsplash.com/photo-1508700115892-45ecd05ae2ad?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "Behind Closed Doors", "author": "B.A. Paris", "isbn": "978-1250121004", "genre": "Thriller",
        "year": 2016, "publisher": "St. Martin's Press", "shelf_location": "THR-02-C",
        "description": "Everyone knows a couple like Jack and Grace. He has looks and wealth; she has charm and elegance. But why does she never answer the front door alone?",
        "cover_image": "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=500&auto=format&fit=crop&q=80",
        "total_copies": 2
    },
    {
        "title": "Before I Go to Sleep", "author": "S.J. Watson", "isbn": "978-0062060563", "genre": "Thriller",
        "year": 2011, "publisher": "Harper", "shelf_location": "THR-03-A",
        "description": "Memories define us. So what if you lost yours every time you went to sleep? Christine wakes each morning not knowing who or where she is.",
        "cover_image": "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=500&auto=format&fit=crop&q=80",
        "total_copies": 2
    },
    {
        "title": "Presumed Innocent", "author": "Scott Turow", "isbn": "978-1455502691", "genre": "Thriller",
        "year": 1987, "publisher": "Farrar, Straus and Giroux", "shelf_location": "THR-03-B",
        "description": "Prosecutor Rozy Sabich is tasked with investigating the murder of his colleague and former lover, only to find the evidence pointing straight at him.",
        "cover_image": "https://images.unsplash.com/photo-1589829085413-56de8ae18c73?w=500&auto=format&fit=crop&q=80",
        "total_copies": 2
    },
    {
        "title": "The Reversal", "author": "Michael Connelly", "isbn": "978-0446401364", "genre": "Thriller",
        "year": 2010, "publisher": "Little, Brown and Company", "shelf_location": "THR-03-C",
        "description": "Defense attorney Mickey Haller switches sides to prosecute a high-profile retrial of a convicted child killer, assisted by detective Harry Bosch.",
        "cover_image": "https://images.unsplash.com/photo-1589829085413-56de8ae18c73?w=500&auto=format&fit=crop&q=80",
        "total_copies": 2
    },
    {
        "title": "Verity", "author": "Colleen Hoover", "isbn": "978-1538724736", "genre": "Thriller",
        "year": 2018, "publisher": "Grand Central Publishing", "shelf_location": "THR-04-A",
        "description": "Lowen Ashleigh is hired to finish the remaining books of an injured author, but in her office she discovers an unpublished manuscript containing bone-chilling admissions.",
        "cover_image": "https://images.unsplash.com/photo-1543002588-bfa74002ed7e?w=500&auto=format&fit=crop&q=80",
        "total_copies": 4
    },

    # Self-Help & Personal Growth
    {
        "title": "Deep Work", "author": "Cal Newport", "isbn": "978-1455586691", "genre": "Self-Help",
        "year": 2016, "publisher": "Grand Central Publishing", "shelf_location": "SH-01-A",
        "description": "Rules for focused success in a distracted world. Mastering the superpower of intense concentration without distraction.",
        "cover_image": "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=500&auto=format&fit=crop&q=80",
        "total_copies": 4
    },
    {
        "title": "The 7 Habits of Highly Effective People", "author": "Stephen R. Covey", "isbn": "978-1982137274", "genre": "Self-Help",
        "year": 1989, "publisher": "Free Press", "shelf_location": "SH-01-B",
        "description": "A holistic, principle-centered approach for solving personal and professional problems based on timeless fairness, integrity, and human dignity.",
        "cover_image": "https://images.unsplash.com/photo-1544717305-2782549b5136?w=500&auto=format&fit=crop&q=80",
        "total_copies": 4
    },
    {
        "title": "Can't Hurt Me", "author": "David Goggins", "isbn": "978-1544512280", "genre": "Self-Help",
        "year": 2018, "publisher": "Lioncrest Publishing", "shelf_location": "SH-01-C",
        "description": "Master your mind and defy the odds: former Navy SEAL David Goggins shares his astonishing life story and the 40% rule to push through pain.",
        "cover_image": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=500&auto=format&fit=crop&q=80",
        "total_copies": 4
    },
    {
        "title": "Essentialism", "author": "Greg McKeown", "isbn": "978-0804137386", "genre": "Self-Help",
        "year": 2014, "publisher": "Crown Business", "shelf_location": "SH-02-A",
        "description": "The disciplined pursuit of less. How to discern what is absolutely essential, eliminate everything else, and make your highest possible contribution.",
        "cover_image": "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "How to Win Friends and Influence People", "author": "Dale Carnegie", "isbn": "978-0671027032", "genre": "Self-Help",
        "year": 1936, "publisher": "Simon & Schuster", "shelf_location": "SH-02-B",
        "description": "Timeless principles of interpersonal relationships, communication empathy, active listening, and sincere leadership.",
        "cover_image": "https://images.unsplash.com/photo-1544717305-2782549b5136?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "Mindset: The New Psychology of Success", "author": "Carol S. Dweck", "isbn": "978-0345472327", "genre": "Self-Help",
        "year": 2006, "publisher": "Ballantine Books", "shelf_location": "SH-02-C",
        "description": "How the belief that abilities can be developed (a growth mindset) fosters resilient learning, outstanding achievement, and personal growth.",
        "cover_image": "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "Grit: The Power of Passion and Perseverance", "author": "Angela Duckworth", "isbn": "978-1501111105", "genre": "Self-Help",
        "year": 2016, "publisher": "Scribner", "shelf_location": "SH-03-A",
        "description": "Pioneering psychologist Angela Duckworth shows that the secret to outstanding achievement is not talent but a special blend of passion and persistence.",
        "cover_image": "https://images.unsplash.com/photo-1517838277536-f5f99be501cd?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "The Power of Habit", "author": "Charles Duhigg", "isbn": "978-0812981605", "genre": "Self-Help",
        "year": 2012, "publisher": "Random House", "shelf_location": "SH-03-B",
        "description": "Why we do what we do in life and business. Investigates the cue-routine-reward habit loop and the neurology behind habit formation.",
        "cover_image": "https://images.unsplash.com/photo-1544717305-2782549b5136?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "Ego is the Enemy", "author": "Ryan Holiday", "isbn": "978-1591847816", "genre": "Self-Help",
        "year": 2016, "publisher": "Portfolio", "shelf_location": "SH-03-C",
        "description": "Drawing on Stoic philosophy and historical examples, Holiday reveals how ego undermines ambition, success, and resilience.",
        "cover_image": "https://images.unsplash.com/photo-1457369804613-52c61a468e7d?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "Drive: The Surprising Truth About What Motivates Us", "author": "Daniel H. Pink", "isbn": "978-1594484803", "genre": "Self-Help",
        "year": 2009, "publisher": "Riverhead Books", "shelf_location": "SH-04-A",
        "description": "Forget carrot-and-stick motivators. The secret to high performance and satisfaction lies in our intrinsic need for autonomy, mastery, and purpose.",
        "cover_image": "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },

    # Romance
    {
        "title": "Normal People", "author": "Sally Rooney", "isbn": "978-1984822178", "genre": "Romance",
        "year": 2018, "publisher": "Faber & Faber", "shelf_location": "ROM-01-A",
        "description": "Connell and Marianne grow up in the same small town in western Ireland, navigating the magnetic intimacy and vulnerabilities of their evolving connection.",
        "cover_image": "https://images.unsplash.com/photo-1516589178581-6cd7833ae3b2?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "The Seven Husbands of Evelyn Hugo", "author": "Taylor Jenkins Reid", "isbn": "978-1501161933", "genre": "Romance",
        "year": 2017, "publisher": "Atria Books", "shelf_location": "ROM-01-B",
        "description": "Aging and reclusive Hollywood movie icon Evelyn Hugo is finally ready to tell the truth about her glamorous and scandalous life and her one true love.",
        "cover_image": "https://images.unsplash.com/photo-1544717305-2782549b5136?w=500&auto=format&fit=crop&q=80",
        "total_copies": 4
    },
    {
        "title": "The Song of Achilles", "author": "Madeline Miller", "isbn": "978-0062060624", "genre": "Romance",
        "year": 2011, "publisher": "Ecco Press", "shelf_location": "ROM-01-C",
        "description": "A lyrical retelling of Homer's Iliad through the intimate perspective of Patroclus, bound by love and destined glory to Prince Achilles.",
        "cover_image": "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=500&auto=format&fit=crop&q=80",
        "total_copies": 4
    },
    {
        "title": "Red, White & Royal Blue", "author": "Casey McQuiston", "isbn": "978-1250316776", "genre": "Romance",
        "year": 2019, "publisher": "St. Martin's Griffin", "shelf_location": "ROM-02-A",
        "description": "What happens when America's First Son falls in love with the Prince of Wales? A sparkling, heartfelt international romance.",
        "cover_image": "https://images.unsplash.com/photo-1516589178581-6cd7833ae3b2?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "Outlander", "author": "Diana Gabaldon", "isbn": "978-0440212560", "genre": "Romance",
        "year": 1991, "publisher": "Delacorte Books", "shelf_location": "ROM-02-B",
        "description": "Claire Randall, a former British combat nurse, steps through a standing stone circle in the Highlands and is catapulted into 1743 Scotland.",
        "cover_image": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "Me Before You", "author": "Jojo Moyes", "isbn": "978-0143124542", "genre": "Romance",
        "year": 2012, "publisher": "Pamela Dorman Books", "shelf_location": "ROM-02-C",
        "description": "Louisa Clark takes a job caring for Will Traynor, a wealthy former banker who is now quadriplegic, sparking a life-changing emotional bond.",
        "cover_image": "https://images.unsplash.com/photo-1516589178581-6cd7833ae3b2?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "Book Lovers", "author": "Emily Henry", "isbn": "978-0593440872", "genre": "Romance",
        "year": 2022, "publisher": "Berkley Books", "shelf_location": "ROM-03-A",
        "description": "A fierce literary agent and an aloof book editor repeatedly cross paths in a tiny North Carolina town in a witty enemies-to-lovers story.",
        "cover_image": "https://images.unsplash.com/photo-1544717305-2782549b5136?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "Beach Read", "author": "Emily Henry", "isbn": "978-1984806734", "genre": "Romance",
        "year": 2020, "publisher": "Berkley Books", "shelf_location": "ROM-03-B",
        "description": "A romance writer who no longer believes in love and a literary author stuck in a rut spend the summer as neighboring rivals.",
        "cover_image": "https://images.unsplash.com/photo-1516589178581-6cd7833ae3b2?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "It Ends with Us", "author": "Colleen Hoover", "isbn": "978-1501110368", "genre": "Romance",
        "year": 2016, "publisher": "Atria Books", "shelf_location": "ROM-03-C",
        "description": "Lily Bloom falls for charming neurosurgeon Ryle Kincaid, but when an old love reappears, she faces impossible choices about love and strength.",
        "cover_image": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500&auto=format&fit=crop&q=80",
        "total_copies": 4
    },
    {
        "title": "The Hating Game", "author": "Sally Thorne", "isbn": "978-0062439604", "genre": "Romance",
        "year": 2016, "publisher": "William Morrow", "shelf_location": "ROM-04-A",
        "description": "Lucy Hutton and Joshua Templeman are executive assistants at a publishing house who despise each other—until they share an elevator ride.",
        "cover_image": "https://images.unsplash.com/photo-1516589178581-6cd7833ae3b2?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },

    # Dystopian
    {
        "title": "Fahrenheit 451", "author": "Ray Bradbury", "isbn": "978-1451673319", "genre": "Dystopian",
        "year": 1953, "publisher": "Ballantine Books", "shelf_location": "DYS-01-A",
        "description": "Guy Montag is a fireman whose job is to burn books, which are forbidden. When he meets an eccentric young neighbor, he begins questioning everything.",
        "cover_image": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "The Handmaid's Tale", "author": "Margaret Atwood", "isbn": "978-0385490818", "genre": "Dystopian",
        "year": 1985, "publisher": "McClelland and Stewart", "shelf_location": "DYS-01-B",
        "description": "In the theocratic Republic of Gilead, Offred is a Handmaid whose sole purpose is to bear children for the ruling elite while remembering her past freedom.",
        "cover_image": "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=500&auto=format&fit=crop&q=80",
        "total_copies": 4
    },
    {
        "title": "The Road", "author": "Cormac McCarthy", "isbn": "978-0307387899", "genre": "Dystopian",
        "year": 2006, "publisher": "Alfred A. Knopf", "shelf_location": "DYS-01-C",
        "description": "A father and his young son walk alone through burned, ash-covered post-apocalyptic America, sustaining the fire of hope.",
        "cover_image": "https://images.unsplash.com/photo-1448375240586-882707db888b?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "Never Let Me Go", "author": "Kazuo Ishiguro", "isbn": "978-1400078776", "genre": "Dystopian",
        "year": 2005, "publisher": "Faber and Faber", "shelf_location": "DYS-02-A",
        "description": "Kathy, Tommy, and Ruth grow up at Hailsham, an idyllic English boarding school, slowly discovering the harrowing truth about their cloned existence.",
        "cover_image": "https://images.unsplash.com/photo-1512820790803-83ca734da794?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "Station Eleven", "author": "Emily St. John Mandel", "isbn": "978-0804172448", "genre": "Dystopian",
        "year": 2014, "publisher": "Alfred A. Knopf", "shelf_location": "DYS-02-B",
        "description": "Twenty years after a flu pandemic collapsed civilization, a traveling troupe of actors and musicians performs Shakespeare for surviving settlements.",
        "cover_image": "https://images.unsplash.com/photo-1516979187457-637abb4f9353?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "Wool", "author": "Hugh Howey", "isbn": "978-1476733951", "genre": "Dystopian",
        "year": 2011, "publisher": "Broad Reach Publishing", "shelf_location": "DYS-02-C",
        "description": "Thousands of people live in a giant underground silo of 144 floors. Outside air is toxic, and anyone who speaks of going outside is sent to clean the sensors.",
        "cover_image": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "Blindness", "author": "Jose Saramago", "isbn": "978-0156007757", "genre": "Dystopian",
        "year": 1995, "publisher": "Editorial Caminho", "shelf_location": "DYS-03-A",
        "description": "A city is hit by an epidemic of 'white blindness'. Quarantined in an asylum, social order rapidly decays as only one woman retains her sight.",
        "cover_image": "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=500&auto=format&fit=crop&q=80",
        "total_copies": 2
    },
    {
        "title": "Parable of the Sower", "author": "Octavia E. Butler", "isbn": "978-1538732182", "genre": "Dystopian",
        "year": 1993, "publisher": "Four Walls Eight Windows", "shelf_location": "DYS-03-B",
        "description": "In 2024 California plagued by climate chaos and societal collapse, Lauren Olamina develops hyperempathy and founds a resilient new faith called Earthseed.",
        "cover_image": "https://images.unsplash.com/photo-1509198397868-475647b2a1e5?w=500&auto=format&fit=crop&q=80",
        "total_copies": 3
    },
    {
        "title": "Children of Men", "author": "P.D. James", "isbn": "978-0307275431", "genre": "Dystopian",
        "year": 1992, "publisher": "Faber & Faber", "shelf_location": "DYS-03-C",
        "description": "In a future England where all human fertility has ceased for two decades, an Oxford historian encounters a small revolutionary group protecting a pregnant woman.",
        "cover_image": "https://images.unsplash.com/photo-1448375240586-882707db888b?w=500&auto=format&fit=crop&q=80",
        "total_copies": 2
    },
    {
        "title": "Feed", "author": "M.T. Anderson", "isbn": "978-0763662622", "genre": "Dystopian",
        "year": 2002, "publisher": "Candlewick Press", "shelf_location": "DYS-04-A",
        "description": "In a consumerist society where internet feeds are hardwired directly into people’s brains, Titus meets Violet, a girl who dares to resist the corporate feed.",
        "cover_image": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=500&auto=format&fit=crop&q=80",
        "total_copies": 2
    }
]

# 20 realistic sample members
SAMPLE_MEMBERS = [
    {"name": "Sophia Patel", "email": "sophia.patel@smartlib.com", "fav": "Science Fiction,Technology,Non-Fiction"},
    {"name": "Liam Chen", "email": "liam.chen@smartlib.com", "fav": "Technology,Science Fiction,Thriller"},
    {"name": "Elena Rostova", "email": "elena.rostova@smartlib.com", "fav": "Fiction,Philosophy,Biography"},
    {"name": "Marcus Vance", "email": "marcus.vance@smartlib.com", "fav": "Mystery,Thriller,Fantasy"},
    {"name": "Aisha Al-Mansoor", "email": "aisha.mansoor@smartlib.com", "fav": "Non-Fiction,Biography,Philosophy"},
    {"name": "Noah Kim", "email": "noah.kim@smartlib.com", "fav": "Technology,Science Fiction,Self-Help"},
    {"name": "Isabella Garcia", "email": "isabella.garcia@smartlib.com", "fav": "Romance,Fiction,Mystery"},
    {"name": "Lucas Dubois", "email": "lucas.dubois@smartlib.com", "fav": "Philosophy,Fiction,History"},
    {"name": "Priya Sharma", "email": "priya.sharma@smartlib.com", "fav": "Technology,Self-Help,Non-Fiction"},
    {"name": "Ethan Wright", "email": "ethan.wright@smartlib.com", "fav": "Fantasy,Science Fiction,Dystopian"},
    {"name": "Zoe Takahashi", "email": "zoe.takahashi@smartlib.com", "fav": "Mystery,Thriller,Dystopian"},
    {"name": "David Miller", "email": "david.miller@smartlib.com", "fav": "Biography,History,Self-Help"},
    {"name": "Chloe Bennett", "email": "chloe.bennett@smartlib.com", "fav": "Romance,Fiction,Fantasy"},
    {"name": "Mateo Rossi", "email": "mateo.rossi@smartlib.com", "fav": "Science Fiction,Technology,Fantasy"},
    {"name": "Fatima Zahra", "email": "fatima.zahra@smartlib.com", "fav": "Non-Fiction,Philosophy,Biography"},
    {"name": "James O'Connor", "email": "james.oconnor@smartlib.com", "fav": "Thriller,Mystery,History"},
    {"name": "Aria Stark", "email": "aria.stark@smartlib.com", "fav": "Fantasy,Fiction,Thriller"},
    {"name": "Daniel Larson", "email": "daniel.larson@smartlib.com", "fav": "Technology,Self-Help,Non-Fiction"},
    {"name": "Hannah Abbott", "email": "hannah.abbott@smartlib.com", "fav": "Romance,Mystery,Fiction"},
    {"name": "Oliver Queen", "email": "oliver.queen@smartlib.com", "fav": "Thriller,Self-Help,Biography"},
]

SAMPLE_REVIEWS = [
    "An absolute masterpiece! Couldn't put it down.",
    "Fascinating concepts, deeply thought-provoking.",
    "Very engaging read, highly recommended for everyone.",
    "Brilliant character development and pacing.",
    "Life-changing ideas that shifted how I think.",
    "A solid read with memorable takeaways.",
    "Gripping plot, kept me guessing until the last page.",
    "Essential reading for anyone interested in this topic.",
    "Incredible storytelling and beautiful prose.",
    "A must-have in every library collection."
]


def seed_database():
    db = SessionLocal()
    try:
        print("Clearing existing data for clean seed...")
        db.query(models.Notification).delete()
        db.query(models.Rating).delete()
        db.query(models.Reservation).delete()
        db.query(models.Loan).delete()
        db.query(models.Book).delete()
        db.query(models.User).delete()
        db.commit()

        print("Creating Admin and Primary Member accounts...")
        # 1. Admin
        admin_user = models.User(
            name="Chief Librarian Admin",
            email="admin@smartlib.com",
            hashed_password=get_password_hash("Admin@123"),
            role="admin",
            membership_status="active",
            borrow_limit=10,
            favorite_genres="All,Science Fiction,Technology,History"
        )
        db.add(admin_user)

        # 2. Member
        primary_member = models.User(
            name="Alex Morgan",
            email="member@smartlib.com",
            hashed_password=get_password_hash("Member@123"),
            role="member",
            membership_status="active",
            borrow_limit=5,
            favorite_genres="Science Fiction,Technology,Mystery"
        )
        db.add(primary_member)

        # 3. 20 Sample Members
        all_members = [primary_member]
        for m_data in SAMPLE_MEMBERS:
            user = models.User(
                name=m_data["name"],
                email=m_data["email"],
                hashed_password=get_password_hash("Password@123"),
                role="member",
                membership_status="active",
                borrow_limit=5,
                favorite_genres=m_data["fav"]
            )
            db.add(user)
            all_members.append(user)
        db.commit()

        print(f"Created {len(all_members)} members + 1 admin.")

        # 4. Insert 100+ Books
        print(f"Adding {len(BOOKS_DATA)} realistic books across 10+ genres...")
        db_books = []
        for b in BOOKS_DATA:
            book_obj = models.Book(
                title=b["title"],
                author=b["author"],
                isbn=b["isbn"],
                genre=b["genre"],
                language="English",
                publisher=b["publisher"],
                year=b["year"],
                description=b["description"],
                cover_image=b["cover_image"],
                total_copies=b["total_copies"],
                available_copies=b["total_copies"],  # will adjust with loans
                shelf_location=b["shelf_location"],
                created_at=datetime.utcnow() - timedelta(days=random.randint(30, 365))
            )
            db.add(book_obj)
            db_books.append(book_obj)
        db.commit()
        print("Books inserted successfully.")

        # 5. Generate 320+ Borrowing Records
        print("Generating 320+ realistic loans, returns, overdue records, and fines...")
        now = datetime.utcnow()
        loans_created = 0

        # We will keep track of active loans per book to adjust available_copies
        active_loans_per_book = {b.id: 0 for b in db_books}

        # Let's seed history loans for each member
        # Historical returned loans (250 items)
        for i in range(250):
            member = random.choice(all_members)
            book = random.choice(db_books)
            days_ago = random.randint(15, 200)
            issue_date = now - timedelta(days=days_ago)
            due_date = issue_date + timedelta(days=14)
            return_date = due_date - timedelta(days=random.randint(-3, 10))

            loan = models.Loan(
                book_id=book.id,
                member_id=member.id,
                issue_date=issue_date,
                due_date=due_date,
                return_date=return_date,
                status="returned",
                renewal_count=random.choice([0, 0, 1]),
                fine_amount=0.0,
                fine_paid=True
            )
            db.add(loan)
            loans_created += 1

        # Active loans (45 items)
        for i in range(45):
            member = random.choice(all_members)
            book = random.choice(db_books)
            if active_loans_per_book[book.id] < book.total_copies:
                issue_date = now - timedelta(days=random.randint(1, 10))
                due_date = issue_date + timedelta(days=14)
                loan = models.Loan(
                    book_id=book.id,
                    member_id=member.id,
                    issue_date=issue_date,
                    due_date=due_date,
                    return_date=None,
                    status="active",
                    renewal_count=random.choice([0, 1]),
                    fine_amount=0.0,
                    fine_paid=False
                )
                db.add(loan)
                active_loans_per_book[book.id] += 1
                loans_created += 1

        # Overdue loans (25 items with Rs. 5 per day fine)
        for i in range(25):
            member = random.choice(all_members)
            book = random.choice(db_books)
            if active_loans_per_book[book.id] < book.total_copies:
                days_overdue = random.randint(2, 12)
                issue_date = now - timedelta(days=14 + days_overdue)
                due_date = issue_date + timedelta(days=14)
                fine = float(days_overdue * settings.FINE_RATE_PER_DAY)
                fine_paid = random.choice([False, False, True])

                loan = models.Loan(
                    book_id=book.id,
                    member_id=member.id,
                    issue_date=issue_date,
                    due_date=due_date,
                    return_date=None,
                    status="overdue",
                    renewal_count=0,
                    fine_amount=fine,
                    fine_paid=fine_paid
                )
                db.add(loan)
                active_loans_per_book[book.id] += 1
                loans_created += 1

        # Specifically ensure primary_member (member@smartlib.com) has:
        # - 2 active loans
        # - 1 overdue loan with fine (Rs. 25)
        # - 3 past returned loans (Dune, Project Hail Mary, Clean Code)
        dune = next(b for b in db_books if b.title == "Dune")
        phm = next(b for b in db_books if b.title == "Project Hail Mary")
        cc = next(b for b in db_books if b.title == "Clean Code")
        ddia = next(b for b in db_books if b.title == "Designing Data-Intensive Applications")
        hound = next(b for b in db_books if b.title == "The Hound of the Baskervilles")
        habits = next(b for b in db_books if b.title == "Atomic Habits")

        # Returned
        for bk in [dune, phm, cc]:
            db.add(models.Loan(
                book_id=bk.id,
                member_id=primary_member.id,
                issue_date=now - timedelta(days=40),
                due_date=now - timedelta(days=26),
                return_date=now - timedelta(days=28),
                status="returned",
                renewal_count=0,
                fine_amount=0.0,
                fine_paid=True
            ))
            loans_created += 1

        # Active for primary member
        db.add(models.Loan(
            book_id=ddia.id,
            member_id=primary_member.id,
            issue_date=now - timedelta(days=5),
            due_date=now + timedelta(days=9),
            status="active",
            renewal_count=0,
            fine_amount=0.0,
            fine_paid=False
        ))
        active_loans_per_book[ddia.id] += 1
        loans_created += 1

        # Overdue for primary member (due 4 days ago -> Rs. 20 fine)
        db.add(models.Loan(
            book_id=hound.id,
            member_id=primary_member.id,
            issue_date=now - timedelta(days=18),
            due_date=now - timedelta(days=4),
            status="overdue",
            renewal_count=0,
            fine_amount=20.0,
            fine_paid=False
        ))
        active_loans_per_book[hound.id] += 1
        loans_created += 1

        # Update available copies for all books
        for bk in db_books:
            active_cnt = active_loans_per_book.get(bk.id, 0)
            bk.available_copies = max(0, bk.total_copies - active_cnt)

        db.commit()
        print(f"Total loans created: {loans_created}")

        # 6. Generate 160+ Ratings & Reviews
        print("Generating 160+ ratings & reviews for collaborative filtering...")
        ratings_created = 0
        rated_pairs = set()

        # High ratings from Alex Morgan for anchor books
        for bk, score, rev in [
            (dune, 5, "Astounding worldbuilding and timeless political depth."),
            (phm, 5, "Brilliant hard sci-fi filled with optimism and humor!"),
            (cc, 4, "Essential software engineering patterns.")
        ]:
            db.add(models.Rating(
                book_id=bk.id,
                member_id=primary_member.id,
                rating=score,
                review_text=rev,
                created_at=now - timedelta(days=25)
            ))
            rated_pairs.add((primary_member.id, bk.id))
            ratings_created += 1

        for _ in range(160):
            member = random.choice(all_members)
            book = random.choice(db_books)
            pair = (member.id, book.id)
            if pair not in rated_pairs:
                score = random.choices([3, 4, 5, 2], weights=[20, 45, 30, 5])[0]
                rev = random.choice(SAMPLE_REVIEWS) if random.random() > 0.4 else None
                db.add(models.Rating(
                    book_id=book.id,
                    member_id=member.id,
                    rating=score,
                    review_text=rev,
                    created_at=now - timedelta(days=random.randint(1, 100))
                ))
                rated_pairs.add(pair)
                ratings_created += 1

        db.commit()
        print(f"Total ratings created: {ratings_created}")

        # 7. Add sample Reservations
        print("Adding sample FIFO reservations...")
        # Make one book unavailable and reserve it
        three_body = next(b for b in db_books if b.title == "The Three-Body Problem")
        db.add(models.Reservation(
            book_id=three_body.id,
            member_id=primary_member.id,
            reserved_at=now - timedelta(days=2),
            status="pending"
        ))
        # Another reservation queued behind Alex
        db.add(models.Reservation(
            book_id=three_body.id,
            member_id=all_members[1].id,
            reserved_at=now - timedelta(days=1),
            status="pending"
        ))
        # Ready reservation for testing pickup hold
        db.add(models.Reservation(
            book_id=habits.id,
            member_id=primary_member.id,
            reserved_at=now - timedelta(days=3),
            status="ready",
            ready_until=now + timedelta(hours=36)
        ))

        # 8. Notifications
        print("Adding initial in-app notifications...")
        db.add(models.Notification(
            user_id=primary_member.id,
            title="Book Overdue Alert",
            message="Your loan for 'The Hound of the Baskervilles' is overdue. Current fine: Rs. 20.00.",
            type="overdue",
            created_at=now - timedelta(hours=8)
        ))
        db.add(models.Notification(
            user_id=primary_member.id,
            title="Reserved Book Ready for Pickup",
            message="'Atomic Habits' is ready for collection at the counter. Held for 36 hours.",
            type="reservation_ready",
            created_at=now - timedelta(hours=14)
        ))
        db.commit()

        print("Training Recommender Engine with freshly seeded dataset...")
        recommender.build_models(db)
        print("SUCCESS: Database seeding and model training completed!")

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
