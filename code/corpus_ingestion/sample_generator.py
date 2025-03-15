"""
Sample data generator for testing the RAG Writing Assistant

This script creates sample text files that mimic the user's writing style
for testing the corpus ingestion and RAG functionality.
"""

import os
import random

# Ensure the sample data directory exists
SAMPLE_DIR = "/home/ubuntu/rag_writing_assistant/sample_data"
os.makedirs(SAMPLE_DIR, exist_ok=True)

# Sample content types and tags
CONTENT_TYPES = {
    "essay": ["education", "technology", "philosophy", "ethics", "future"],
    "reflection": ["personal", "growth", "experience", "learning", "insight"],
    "podcast": ["interview", "discussion", "analysis", "trends", "innovation"],
    "substack": ["newsletter", "update", "analysis", "opinion", "review"]
}

# Sample paragraphs for different content types
SAMPLE_PARAGRAPHS = {
    "essay": [
        "The intersection of artificial intelligence and education represents one of the most promising frontiers in modern learning. As we stand at this technological crossroads, it's crucial to consider not just the efficiency gains but the fundamental transformation of how knowledge is transmitted and internalized. The traditional classroom model, largely unchanged for centuries, may soon give way to personalized learning experiences that adapt in real-time to each student's needs, strengths, and weaknesses.",
        
        "Critical thinking remains the cornerstone of meaningful education. In an era of abundant information and algorithmic curation, the ability to evaluate sources, question assumptions, and synthesize diverse perspectives becomes increasingly valuable. Educational institutions must prioritize these skills alongside technical competencies, fostering minds that can navigate complexity rather than merely absorb facts.",
        
        "The ethical dimensions of technological integration in education cannot be overlooked. Questions of privacy, algorithmic bias, and equitable access demand thoughtful consideration. As we build these new systems, we must ensure they serve to democratize knowledge rather than reinforce existing inequalities. This requires intentional design choices guided by diverse voices and perspectives.",
        
        "Looking toward the future, we might envision learning environments that seamlessly blend physical and digital realms, where AI tutors collaborate with human teachers to create rich, multifaceted educational experiences. The goal should not be to replace human connection but to enhance it, creating space for deeper engagement with ideas and with one another."
    ],
    
    "reflection": [
        "Yesterday's conversation with Dr. Chen fundamentally shifted my perspective on machine learning ethics. I've long approached the field from a primarily technical standpoint, focusing on model accuracy and computational efficiency. Her emphasis on the lived experiences of communities affected by algorithmic decision-making systems reminded me that behind every data point lies a human story.",
        
        "I find myself increasingly drawn to the liminal spaces between disciplines. The most interesting questions seem to emerge not from the center of established fields but from their overlapping boundaries. This intellectual borderland requires a certain comfort with ambiguity, a willingness to speak multiple academic languages imperfectly rather than a single one fluently.",
        
        "The writing process continues to surprise me after all these years. What begins as a clear, linear argument inevitably transforms as it meets the page. Ideas connect in unexpected ways, revealing patterns I hadn't consciously recognized. There's a dialogue between my conscious intentions and something deeper, a conversation that unfolds through the act of writing itself.",
        
        "I'm learning to embrace the iterative nature of creative work. The perfect is indeed the enemy of the good, and waiting for fully-formed brilliance often results in nothing at all. Better to create something imperfect, to put ideas into the world where they can breathe and evolve through engagement with others."
    ],
    
    "podcast": [
        "Welcome to another episode of Future Thinkers, where we explore the ideas shaping tomorrow's world. I'm your host, and today we're diving into the fascinating realm of synthetic biology with Dr. Sarah Mendez, whose groundbreaking work at the intersection of genetic engineering and computational design is opening new possibilities for addressing climate change.",
        
        "Before we jump into our conversation, I want to thank our listeners for the thoughtful questions submitted after last week's episode on digital governance. Your engagement makes this podcast a truly collaborative exploration, and we'll be addressing several of your points during today's discussion.",
        
        "Dr. Mendez approaches her research with both scientific rigor and ethical nuance, qualities that have earned her recognition as a leading voice in responsible innovation. Our conversation will cover not just the technical aspects of her work but also the philosophical questions it raises about humanity's relationship with the natural world.",
        
        "As we consider the potential of these emerging technologies, we'll be asking not just what we can do, but what we should do. These questions have no easy answers, but the conversation itself is essential as we collectively navigate this period of unprecedented technological change."
    ],
    
    "substack": [
        "In this week's newsletter, we're examining the recent developments in decentralized finance that have largely flown under the mainstream radar. While headlines focus on cryptocurrency price fluctuations, the more significant innovation is happening in governance structures that could fundamentally reshape how financial systems operate.",
        
        "Several readers responded to last week's piece on digital privacy with thoughtful critiques of my position on regulatory approaches. Your points about the limitations of GDPR-style frameworks in global contexts were particularly insightful, and they've prompted me to reconsider certain aspects of my analysis.",
        
        "The most compelling book I've encountered this month is Professor Alicia Wong's 'Networks of Meaning,' which offers a fresh theoretical framework for understanding how information spreads through social systems. Her integration of complexity science with traditional media theory provides valuable tools for analyzing our current information ecosystem.",
        
        "Looking ahead, I'll be attending the Technology Ethics Symposium in Copenhagen next month and would love to connect with any subscribers who will be there. These conversations are always richer in person, and I'm particularly interested in hearing your perspectives on the topics we've been exploring in this newsletter."
    ]
}

def generate_sample_files(num_files=20):
    """Generate sample text files for testing"""
    
    for i in range(1, num_files + 1):
        # Randomly select content type
        content_type = random.choice(list(CONTENT_TYPES.keys()))
        
        # Select 1-3 random tags for this content type
        tags = random.sample(CONTENT_TYPES[content_type], k=min(3, len(CONTENT_TYPES[content_type])))
        
        # Create a title
        titles = {
            "essay": [
                "The Future of Learning in an AI-Driven World",
                "Ethical Considerations in Technological Education",
                "Reimagining Knowledge Transfer in the Digital Age",
                "Critical Thinking in an Era of Information Abundance",
                "The Evolution of Educational Paradigms"
            ],
            "reflection": [
                "Thoughts on Interdisciplinary Approaches",
                "Finding Meaning in Intellectual Exploration",
                "Personal Growth Through Creative Challenge",
                "Reconsidering My Approach to Problem Solving",
                "Lessons from a Year of Deliberate Practice"
            ],
            "podcast": [
                "Introducing Today's Conversation on Innovation",
                "Exploring the Frontiers of Synthetic Biology",
                "Welcome to Our Discussion on Digital Governance",
                "Setting the Stage for Today's Interview",
                "Opening Thoughts on Technological Transformation"
            ],
            "substack": [
                "Weekly Analysis: Trends in Decentralized Systems",
                "Reader Responses and Further Thoughts",
                "Book Recommendations and Theoretical Frameworks",
                "Upcoming Events and Connection Opportunities",
                "Deep Dive: Understanding Emergent Technologies"
            ]
        }
        
        title = random.choice(titles[content_type])
        
        # Format filename
        filename = f"{content_type.capitalize()} - {title} [{', '.join(tags)}].txt"
        file_path = os.path.join(SAMPLE_DIR, filename)
        
        # Generate content - select 4-8 paragraphs
        num_paragraphs = random.randint(4, 8)
        paragraphs = []
        
        # Add a metadata header sometimes
        if random.choice([True, False]):
            metadata = f"""Title: {title}
Date: 2024-{random.randint(1, 12):02d}-{random.randint(1, 28):02d}
Tags: {', '.join(tags)}
Type: {content_type.capitalize()}
Summary: A sample {content_type} about {random.choice(tags)}.

"""
            paragraphs.append(metadata)
        
        # Add content paragraphs
        for _ in range(num_paragraphs):
            paragraphs.append(random.choice(SAMPLE_PARAGRAPHS[content_type]))
        
        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("\n\n".join(paragraphs))
        
        print(f"Created sample file: {filename}")

if __name__ == "__main__":
    generate_sample_files()
    print(f"Sample data generation complete. Files saved to {SAMPLE_DIR}")
