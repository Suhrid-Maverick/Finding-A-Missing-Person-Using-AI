## AI-Powered Missing Person Identification & Recovery System
## 📖 Table of Contents
- [Overview](#overview)
- [Key Features](#key-features)
- [Screenshots & Walkthrough](#screenshots--walkthrough)
- [Tech Stack](#tech-stack)
- [How It Works (ML Pipeline)](#how-it-works-ml-pipeline)
- [Installation & Setup](#installation--setup)
- [Usage Guide](#usage-guide)
- [Project Structure](#project-structure)
- [Future Roadmap](#future-roadmap)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

---

## 🔭 Overview

Every year, millions of individuals go missing worldwide. Traditional search methods often suffer from fragmented data, delayed communication, and a lack of analytical tools. **FindTrack AI** bridges this gap by offering:

- **Centralized Case Management**: A unified dashboard for submitting, updating, and tracking cases.
- **AI-Driven Facial Matching**: Instant comparison of uploaded photos against a growing database of missing persons and public sightings.
- **Spatial Analysis**: Interactive heatmaps and bubble maps that highlight geographic hotspots of unresolved cases.
- **Public Participation**: A secure "Report a Sighting" portal allowing citizens to safely contribute tips and media.

---

## ✨ Key Features

| Module | Description |
| :--- | :--- |
| **Register New Case** | Submit a missing person report with personal details, physical markers (birthmarks, scars), and a high-resolution photo. |
| **All Cases Dashboard** | View all submitted cases with advanced filters (status, name, date). Export data to CSV for offline analysis. |
| **AI Match Cases** | Run the matching engine to detect potential duplicates or connect a sighting to an existing case. |
| **Interactive World Map** | Visualize cases globally. Circle size = number of cases per city. Color coding (Red/Green) indicates unresolved vs. resolved status. |
| **Report a Sighting** | Anonymous or verified users can upload images/videos of potential sightings (up to 200MB per file). |
| **Geographic Filters** | Drill down into specific regions (e.g., "India Map", "Cities without coordinates" alerts). |

---

## 🖼️ Screenshots & Walkthrough

Below is a detailed walkthrough of the application interface, demonstrating how users interact with the AI system.

### 1. Home Dashboard – Overview & Stats
<img width="1919" height="1016" alt="Screenshot 2026-08-18 062429" src="https://github.com/user-attachments/assets/2c67c1a7-507b-4e0a-8920-ead4cf6bb7b8" />

The **Home** screen serves as the central command center. Upon login, administrators see a highlighted missing person case (e.g., "Suhrid Paul") at the top, along with quick stats like "Found Cases Count" and "Not Found Cases Count".

- **Key Elements**: 
  - Navigation sidebar (Home, Register New Case, All Cases, Match Cases, Map).
  - A dynamic **Cases by City** heatmap of India, with major cities like Delhi, Kolkata, Mumbai, and Hyderabad clearly marked.
  - Quick access to the Admin panel and Logout.
- **AI Insight**: The dashboard uses clustering algorithms to display aggregate case densities, helping authorities allocate resources effectively.

---

### 2. Geographic Focus – India Map View
<img width="1919" height="1018" alt="Screenshot 2026-08-18 062458" src="https://github.com/user-attachments/assets/741c8529-4792-4e97-bb1e-df8141827189" />

This detailed zoomed-in view focuses specifically on the Indian subcontinent.

- **Key Elements**:
  - Interactive markers for cities such as Jaipur, Kanpur, Varanasi, Patna, Ahmedabad, Bhopal, Surat, Nagpur, Bhilai, Visakhapatnam, Bengaluru, Chennai, Coimbatore, and Madurai.
  - Integration with **Leaflet / OpenStreetMap** for seamless pan and zoom.
- **AI Insight**: The system geoparses textual location inputs (e.g., "Kothri Kalan") and converts them into precise coordinates, alerting users if a city lacks map coordinates (e.g., "Madhya Pradesh" warning) to prevent data loss.

---

### 3. Global Surveillance – World Map Monitoring
<img width="1919" height="1015" alt="Screenshot 2026-08-18 062506" src="https://github.com/user-attachments/assets/ff23acd9-e1a4-478d-a7e8-c0c4692c4c72" />

Beyond India, FindTrack AI provides a macro-level **World Map** for tracking transnational missing person networks.

- **Key Elements**:
  - Countries visualized: Ethiopia, Sudan, Sri Lanka, Malaysia, Kenya, Rwanda, Indonesia, Tanzania, Papua New Guinea, Mozambique.
  - **Legend**: "Has unresolved cases" (Red/Yellow) vs. "All cases resolved" (Green).
  - **Circle size = number of cases**, providing immediate visual weight.
  - Sidebar panel for "City Summary" displaying totals (Total, Found, Not Found).
- **AI Insight**: The spatial database uses geographic information system (GIS) logic to rank regions by urgency, prioritizing areas with high unresolved case clusters.

---

### 4. Register New Case – Data Entry Portal
<img width="1919" height="1014" alt="Screenshot 2026-08-18 062435" src="https://github.com/user-attachments/assets/95b7599a-f685-4f33-a699-9b21e8cd5308" />

This form is the entry point for new missing person reports.

- **Key Elements**:
  - Clean, user-friendly layout with fields for personal details.
  - **Upload Photo** section with a clear call-to-action button. Supports JPG and PNG formats.
  - File limit: **200MB per file**, allowing for high-resolution images crucial for facial recognition accuracy.
- **AI Insight**: Uploaded images are immediately preprocessed (face detection, alignment, and normalization) before being stored as 512-dimensional embedding vectors in the feature database.

---

### 5. Report a Sighting – Public Submission
<img width="1919" height="1014" alt="Screenshot 2026-08-18 062515" src="https://github.com/user-attachments/assets/0cfe9150-33ff-4943-b7ed-348ddf2dca3e" />

This module empowers the general public to contribute safely to the search effort.

- **Key Elements**:
  - **Upload type**: Radio toggle between "Image" and "Video".
  - Drag-and-drop or click-to-upload interface.
  - Strict validation (200MB limit, JPG/PNG for images).
- **AI Insight**: Unlike case registration, sighting images are run through a **real-time inference pipeline**. They are compared against all open cases instantly. If the similarity score exceeds a dynamic threshold (e.g., >85%), an alert is pushed to the case manager.

---

### 6. AI Match Cases – The Matching Engine
<img width="1919" height="1011" alt="Screenshot 2026-08-18 062449" src="https://github.com/user-attachments/assets/ff156507-97cd-4af5-9e02-d75bf9db479a" />

The core of the AI functionality is accessed here.

- **Key Elements**:
  - "Check for Match" button—activates the model inference.
  - "Refresh" button—resyncs with the latest database entries.
- **AI Insight**: This screen triggers a Siamese Neural Network or ArcFace model to compute pairwise cosine distances between the query image and all database embeddings. The system returns ranked results, indicating potential matches even under variations in lighting, age, or facial hair.

---

### 7. View Submitted Cases – Management & Filtering
<img width="1919" height="1013" alt="Screenshot 2026-08-18 062443" src="https://github.com/user-attachments/assets/d373d0d6-5277-4f7e-8d6f-1deae3c67a1a" />

A data-rich table allows for granular case management.

- **Key Elements**:
  - **Filter by Status**: "All", "Found", or "Not Found".
  - **Search by Name** and **Filter by Date** (YYYY/MM/DD).
  - **Download as CSV** for external reporting.
  - **Detailed Example**: *Suhrid Paul (Age: 21)* – Status: **Found**.
    - *Last Seen*: 14th August, 2026.
    - *Location*: Kothri Kalan.
    - *Submitted By*: Ananjan Das Poddar (Mobile: 8584027484).
    - *Distinctive Mark*: "Right leg fourth finger has a mole."
- **AI Insight**: The system uses Natural Language Processing (NLP) to parse textual descriptions (like birthmarks) and cross-references them with similar text embeddings in other cases, providing a text-based similarity metric alongside visual matching.

---

## 🧠 How It Works (ML Pipeline)

The AI backbone consists of a multi-modal pipeline:

1.  **Data Ingestion**:
    - Structured metadata (Name, Age, Location) is stored in a relational database.
    - Unstructured media (Images, Videos) are stored in cloud/object storage.

2.  **Face Detection & Alignment** (Preprocessing):
    - We utilize **MTCNN (Multi-task Cascaded Convolutional Networks)** or **RetinaFace** to detect faces and crop them from the background.
    - Images are resized to a standard dimension (e.g., 112x112) for embedding extraction.

3.  **Feature Extraction (Embedding)**:
    - A pre-trained **ArcFace** or **FaceNet** model (fine-tuned on a diverse dataset to handle ethnicity and age variations) transforms the face crop into a 512-dimensional floating-point vector.
    - These embeddings are indexed using **FAISS (Facebook AI Similarity Search)** for rapid nearest-neighbor searches across millions of records.

4.  **Geospatial Mapping**:
    - Location strings are geocoded using **Nominatim/OpenStreetMap** APIs.
    - We generate **Folium/Leaflet** maps with marker clustering and heatmap layers.

5.  **Matching Logic**:
    - **Visual Match**: Cosine similarity between embeddings. If distance < threshold, it's a potential match.
    - **Textual Match**: Elasticsearch or BM25 algorithm checks descriptions, birthmarks, and last seen locations for keyword overlap.
    - **Temporal Filter**: Cases reported within a certain time frame of a sighting are weighted higher.

6.  **Feedback Loop**:
    - When a case is marked "Found", the AI uses this as a positive reinforcement signal to update the model's decision boundaries via active learning.

---

## 💻 Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Frontend / UI** | Streamlit (Python) - Rapid prototyping dashboard |
| **Mapping** | Folium, Leaflet.js, OpenStreetMap |
| **Machine Learning** | TensorFlow, Keras, PyTorch (for ArcFace) |
| **Computer Vision** | OpenCV, MTCNN, Dlib |
| **Similarity Search** | FAISS or Scikit-learn (Nearest Neighbors) |
| **Database** | PostgreSQL (for structured data) + AWS S3 (for images) |
| **Geocoding** | Geopy / Nominatim |
| **Deployment** | Streamlit Cloud / AWS EC2 / Docker |

---

## 🚀 Installation & Setup

Follow these steps to run FindTrack AI locally or on your server.

### Prerequisites
- Python 3.9+
- pip & virtualenv
- (Optional) CUDA-compatible GPU for faster inference

### 1. Clone the Repository
```bash
git clone https://github.com/your-org/findtrack-ai.git
cd findtrack-ai
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

*requirements.txt* should contain:
```
streamlit>=1.25.0
tensorflow>=2.10.0
opencv-python-headless
mtcnn
scikit-learn
pandas
numpy
folium
streamlit-folium
Pillow
geopy
```

### 4. Download Pre-trained Model Weights
Place your `face_model.h5` or `arcface_model.pth` in the `models/` directory.
*(We provide a script `download_weights.sh` for automated downloading).*

### 5. Configure Environment Variables
Create a `.env` file:
```
DB_HOST=localhost
DB_USER=admin
DB_PASS=secure_pass
STORAGE_BUCKET=findtrack-data
```

### 6. Run the Application
```bash
streamlit run app.py
```
The dashboard will be accessible at `http://localhost:8501`.

---

## 🕹️ Usage Guide

### For Administrators (NGOs/Police)
1.  **Login**: Access the admin panel via the sidebar.
2.  **Register Case**: Navigate to "Register New Case" -> Fill details -> Upload photo -> Submit.
3.  **Review Sightings**: Check "Report a Sighting" data daily; sighting images are automatically compared against open cases.
4.  **Update Status**: In "All Cases", search for a person and toggle status to "Found". This removes them from the active matching pool.
5.  **Deploy Resources**: Use the "Map" to view high-density unresolved zones and direct search teams accordingly.

### For General Public (Citizens)
1.  **Report a Sighting**: Open the public URL -> Select "Image" or "Video" -> Upload the media.
2.  *Note*: If the AI detects a high-confidence match, the system will instantly ask the reporter to confirm details without revealing sensitive case data.

---

## 🛣️ Future Roadmap

- **Real-Time Video Surveillance**: Integrating with CCTV feeds to automatically detect missing persons in public places.
- **Age Progression**: GAN-based models to simulate how a missing child might look after several years.
- **Mobile App**: Dedicated iOS/Android applications for field workers with offline capabilities.
- **Multi-Language Support**: NLP for Hindi, Tamil, and other regional languages to improve rural accessibility.
- **Blockchain Verification**: Immutable timestamping of sightings to prevent tampering of evidence.

---

## 🤝 Contributing

We welcome contributions from the community, especially:
- Data augmentation for underrepresented demographics.
- Security audits for the public submission portal.
- Optimizations for low-power edge devices.

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/AmazingFeature`).
3. Commit changes (`git commit -m 'Add some AmazingFeature'`).
4. Push to branch (`git push origin feature/AmazingFeature`).
5. Open a Pull Request.
---

*"Every missing person is a story waiting to be reunited. Let's use AI to bring them home."*
