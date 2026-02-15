/**
 * Landing Page Footer
 * Professional multi-column footer with dark theme.
 * Uses Flexbox for responsive 4-column → 1-column layout.
 */

export function LandingFooter() {
    return (
        <footer className="landing-footer">
            <div className="container landing-footer-grid">
                {/* Column 1: Brand */}
                <div className="landing-footer-col">
                    <div className="landing-footer-brand">
                        <svg
                            width="28"
                            height="28"
                            viewBox="0 0 24 24"
                            fill="currentColor"
                            className="landing-footer-icon"
                        >
                            <path d="M4.5 9.5a2.5 2.5 0 1 1 0-5 2.5 2.5 0 0 1 0 5Zm15 0a2.5 2.5 0 1 1 0-5 2.5 2.5 0 0 1 0 5ZM8 14a2.5 2.5 0 1 1 0-5 2.5 2.5 0 0 1 0 5Zm8 0a2.5 2.5 0 1 1 0-5 2.5 2.5 0 0 1 0 5Zm-4 7a3.5 3.5 0 1 1 0-7 3.5 3.5 0 0 1 0 7Z" />
                        </svg>
                        <span className="landing-footer-logo-text">Vet Clinic</span>
                    </div>
                    <p className="landing-footer-tagline">
                        Compassionate care for your furry family members. Trusted by pet
                        owners since 2020.
                    </p>
                </div>

                {/* Column 2: Services */}
                <div className="landing-footer-col">
                    <h4 className="landing-footer-heading">Services</h4>
                    <ul className="landing-footer-list">
                        <li>
                            <a href="#" className="landing-footer-link">Wellness Exams</a>
                        </li>
                        <li>
                            <a href="#" className="landing-footer-link">Vaccinations</a>
                        </li>
                        <li>
                            <a href="#" className="landing-footer-link">Surgery</a>
                        </li>
                    </ul>
                </div>

                {/* Column 3: Contact */}
                <div className="landing-footer-col">
                    <h4 className="landing-footer-heading">Contact</h4>
                    <ul className="landing-footer-list">
                        <li className="landing-footer-info">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
                                <circle cx="12" cy="10" r="3" />
                            </svg>
                            123 Pawsome Lane, Manila
                        </li>
                        <li>
                            <a href="tel:+639171234567" className="landing-footer-link landing-footer-info">
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                    <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z" />
                                </svg>
                                +63 917 123 4567
                            </a>
                        </li>
                        <li className="landing-footer-info">
                            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <circle cx="12" cy="12" r="10" />
                                <polyline points="12 6 12 12 16 14" />
                            </svg>
                            Mon–Sat, 8:00 AM – 6:00 PM
                        </li>
                    </ul>
                </div>

                {/* Column 4: Emergency */}
                <div className="landing-footer-col">
                    <h4 className="landing-footer-heading">Emergency</h4>
                    <p className="landing-footer-emergency-text">
                        Need urgent care outside clinic hours? Our emergency line is available 24/7.
                    </p>
                    <a href="tel:+639171234567" className="landing-footer-emergency-link">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z" />
                        </svg>
                        After-Hours Emergency
                    </a>
                </div>
            </div>

            {/* Bottom Bar */}
            <div className="landing-footer-bottom">
                <div className="container landing-footer-bottom-inner">
                    <span>&copy; 2026 Vet Clinic. All rights reserved.</span>
                    <div className="landing-footer-bottom-links">
                        <a href="#" className="landing-footer-link">Privacy Policy</a>
                        <a href="#" className="landing-footer-link">Terms of Service</a>
                    </div>
                </div>
            </div>
        </footer>
    );
}
