import ChatWidget from "./components/ChatWidget";
import "./App.css";

function App() {
  return (
    <main className="app">

      {/* =====================================================
          BACKGROUND EFFECTS
          ===================================================== */}

      <div className="background-glow background-glow-one" />
      <div className="background-glow background-glow-two" />

      {/* =====================================================
          NAVIGATION
          ===================================================== */}

      <nav className="navbar">

        <div className="brand">
          <div className="brand-icon">
            AI
          </div>

          <span>
            MoinSystems
          </span>
        </div>

        <div className="nav-status">
          <span className="nav-status-dot" />
          AI Assistant Online
        </div>

      </nav>


      {/* =====================================================
          HERO
          ===================================================== */}

      <section className="hero-section">

        <div className="hero-content">

          <div className="hero-badge">
            <span className="badge-dot" />
            AI-Powered Solutions
          </div>

          <h1>
            Build smarter.
            <br />

            <span className="gradient-text">
              Think with AI.
            </span>
          </h1>

          <p className="hero-description">
            Intelligent digital solutions designed to help
            businesses automate workflows, understand data,
            and build better products.
          </p>


          {/* =================================================
              CTA BUTTONS
              ================================================= */}

          <div className="hero-actions">

            <button
              type="button"
              className="primary-button"
              onClick={() => {
                document
                  .querySelector<HTMLButtonElement>(
                    ".chat-launcher",
                  )
                  ?.click();
              }}
            >
              <span>Talk to MoinSystems AI</span>
              <span className="button-arrow">
                →
              </span>
            </button>

            <button
              type="button"
              className="secondary-button"
              onClick={() => {
                document
                  .querySelector(".services-section")
                  ?.scrollIntoView({
                    behavior: "smooth",
                  });
              }}
            >
              Explore Services
            </button>

          </div>


          {/* =================================================
              TRUST
              ================================================= */}

          <div className="hero-trust">

            <div className="trust-avatars">
              <span>AI</span>
              <span>ML</span>
              <span>DX</span>
            </div>

            <div>
              <strong>Intelligent by design</strong>
              <small>
                AI • Automation • Digital Solutions
              </small>
            </div>

          </div>

        </div>


        {/* =================================================
            HERO VISUAL
            ================================================= */}

        <div className="hero-visual">

          <div className="orb orb-one" />
          <div className="orb orb-two" />

          <div className="ai-card">

            <div className="ai-card-header">

              <div className="ai-card-title">
                <div className="mini-ai-icon">
                  AI
                </div>

                <div>
                  <strong>
                    MoinSystems AI
                  </strong>

                  <span>
                    Intelligent Assistant
                  </span>
                </div>
              </div>

              <span className="online-pill">
                <span />
                Online
              </span>

            </div>


            <div className="ai-card-body">

              <div className="fake-message assistant-message">
                <div className="message-icon">
                  AI
                </div>

                <div>
                  How can I help you today?
                </div>
              </div>

              <div className="fake-message user-message">
                Tell me about your AI services.
              </div>

              <div className="fake-message assistant-message">

                <div className="message-icon">
                  AI
                </div>

                <div>
                  We build intelligent solutions using
                  modern AI and automation technologies.
                </div>

              </div>

            </div>


            <div className="ai-card-input">

              <span>
                Ask anything...
              </span>

              <div className="fake-send">
                →
              </div>

            </div>

          </div>

        </div>

      </section>


      {/* =====================================================
          SERVICES
          ===================================================== */}

      <section
        className="services-section"
        id="services"
      >

        <div className="section-heading">

          <span className="section-label">
            WHAT WE DO
          </span>

          <h2>
            Technology that
            <span className="gradient-text">
              {" "}moves you forward.
            </span>
          </h2>

          <p>
            From intelligent automation to AI-powered
            applications, we turn complex problems into
            simple digital experiences.
          </p>

        </div>


        <div className="service-grid">

          <article className="service-card">

            <div className="service-icon purple">
              ✦
            </div>

            <h3>
              Artificial Intelligence
            </h3>

            <p>
              AI-powered applications designed to automate
              tasks and deliver intelligent insights.
            </p>

            <span className="card-link">
              Explore AI →
            </span>

          </article>


          <article className="service-card">

            <div className="service-icon cyan">
              ◈
            </div>

            <h3>
              Machine Learning
            </h3>

            <p>
              Predictive models and data-driven systems
              built around real-world business needs.
            </p>

            <span className="card-link">
              Explore ML →
            </span>

          </article>


          <article className="service-card">

            <div className="service-icon blue">
              ◎
            </div>

            <h3>
              Digital Solutions
            </h3>

            <p>
              Modern software solutions that improve
              workflows, productivity, and customer experience.
            </p>

            <span className="card-link">
              Explore Solutions →
            </span>

          </article>

        </div>

      </section>


      {/* =====================================================
          AI CTA
          ===================================================== */}

      <section className="ai-cta">

        <div className="cta-glow" />

        <div className="cta-content">

          <div className="cta-icon">
            ✦
          </div>

          <div>

            <span className="section-label">
              NEED ASSISTANCE?
            </span>

            <h2>
              Have a question?
              <span className="gradient-text">
                {" "}Ask our AI.
              </span>
            </h2>

            <p>
              Our AI assistant is ready to help you
              understand our services and solutions.
            </p>

          </div>

          <button
            type="button"
            className="primary-button cta-button"
            onClick={() => {
              document
                .querySelector<HTMLButtonElement>(
                  ".chat-launcher",
                )
                ?.click();
            }}
          >
            Start Conversation →
          </button>

        </div>

      </section>


      {/* =====================================================
          FOOTER
          ===================================================== */}

      <footer className="footer">

        <div className="brand footer-brand">

          <div className="brand-icon">
            AI
          </div>

          <span>
            MoinSystems
          </span>

        </div>

        <p>
          Intelligent technology for a smarter future.
        </p>

        <span className="footer-copy">
          © 2026 MoinSystems. All rights reserved.
        </span>

      </footer>


      {/* =====================================================
          CHATBOT
          ===================================================== */}

      <ChatWidget />

    </main>
  );
}

export default App;