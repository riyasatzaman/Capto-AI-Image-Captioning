# Capto - AI Image Captioning

Capto is an AI-powered web application that transforms your images into creative, descriptive captions. Built using Flask and leveraging advanced computer vision and natural language processing technologies, Capto offers a modern, responsive, and user-friendly experience. With features like multiple caption styles, smooth animations, and a sleek dark/light mode toggle, Capto simplifies content creation and enhances the way you share your visual stories.

## Features

- **AI-Powered Captioning:** Automatically generate high-quality captions using advanced AI.
- **Multiple Caption Styles:** Choose from default, funny, poetic, witty, or formal styles.
- **Modern UI:** Enjoy a professionally designed landing page with smooth animations and responsive design.
- **Dark/Light Mode:** Seamlessly switch between dark and light themes.
- **Easy Setup & Deployment:** Get started quickly with a straightforward setup process.

## Setup Process

Follow these steps to set up Capto on your local machine:

1. **Clone the Repository:**
   ```bash
   git clone https://github.com/riyasatzaman/Capto-AI-Image-Captioning.git
    ```
2. **Navigate to the Project Directory:**
   ```bash
   cd Capto-AI-Image-Captioning
    ```
3. **Create a Virtual Environment:**
   ```bash
   python -m venv venv
    ```
4. **Activate the Virtual Environment:**
- **Windows:**
  ```
  venv\Scripts\activate
  ```
- **macOS/Linux:**
  ```
  source venv/bin/activate
  ```
5. **Install Dependencies:**
  ```
  pip install -r requirements.txt
  ```
6. **Run the Flask App:**
  ```
  python app.py
  ```
7. **Open Your Browser:**
Visit [http://127.0.0.1:5000](http://127.0.0.1:5000) to see Capto in action.

## Deployment

To deploy Capto for free on the internet, consider using services like [Render](https://render.com) or [Heroku](https://www.heroku.com). Make sure your `requirements.txt` is up-to-date and add a `Procfile` (if necessary) with the following content:

  ```
  web: gunicorn app:app
  ```
## License

This project is licensed under the [MIT License](LICENSE).

## Contact

For inquiries or support, please reach out to:
- **Email:** [riyasatzaman@gmail.com](mailto:riyasatzaman@gmail.com)
- **GitHub:** [@riyasatzaman](https://github.com/riyasatzaman)

