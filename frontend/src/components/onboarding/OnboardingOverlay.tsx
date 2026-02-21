import { useState, useEffect } from 'react';
import { Button } from '../ui/Button';

interface OnboardingStep {
    title: string;
    description: string;
    icon: React.ReactNode;
}

const STEPS: OnboardingStep[] = [
    {
        title: 'Welcome to Vet Clinic!',
        description: "We're so glad you're here. Let's take a quick tour to help you get started with managing your pets' health.",
        icon: (
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-primary">
                <path d="M6 9a6 6 0 1 0 12 0" />
                <path d="M12 3v6" />
                <path d="m21 9-9 7-9-7" />
                <path d="M3 5h18" />
            </svg>
        ),
    },
    {
        title: 'Register Your Pets',
        description: 'First, add your furry friends. You can store their breed, medical history, and vaccination records all in one place.',
        icon: (
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-secondary">
                <path d="M10 5.172a1 1 0 0 0 .586.914l1.294.647A8 8 0 1 1 20 12v-2" />
                <path d="M16.12 15a3 3 0 1 0-5.49 0" />
                <path d="M12 12h.01" />
                <circle cx="12" cy="12" r="10" />
            </svg>
        ),
    },
    {
        title: 'Schedule Appointments',
        description: 'Ready for a visit? Booking an appointment is easy. Choose your pet, select a service, and find a time that works for you.',
        icon: (
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-success">
                <rect width="18" height="18" x="3" y="4" rx="2" ry="2" />
                <line x1="16" y1="2" x2="16" y2="6" />
                <line x1="8" y1="2" x2="8" y2="6" />
                <line x1="3" y1="10" x2="21" y2="10" />
            </svg>
        ),
    },
    {
        title: 'Your Dashboard',
        description: 'Keep track of everything at a glance. See upcoming appointments, your pets, and the clinic status from your personal dashboard.',
        icon: (
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-purple">
                <rect width="7" height="9" x="3" y="3" rx="1" />
                <rect width="7" height="5" x="14" y="3" rx="1" />
                <rect width="7" height="9" x="14" y="12" rx="1" />
                <rect width="7" height="5" x="3" y="16" rx="1" />
            </svg>
        ),
    },
    {
        title: "You're All Set!",
        description: "Now you're ready to explore. Head to your dashboard and add your first pet to begin!",
        icon: (
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-info">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                <polyline points="22 4 12 14.01 9 11.01" />
            </svg>
        ),
    },
];

export function OnboardingOverlay() {
    const [currentStep, setCurrentStep] = useState(0);
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        const isCompleted = localStorage.getItem('onboarding_completed');
        if (!isCompleted) {
            setIsVisible(true);
            document.body.style.overflow = 'hidden';
        }
    }, []);

    const handleNext = () => {
        if (currentStep < STEPS.length - 1) {
            setCurrentStep(currentStep + 1);
        } else {
            completeOnboarding();
        }
    };

    const handleBack = () => {
        if (currentStep > 0) {
            setCurrentStep(currentStep - 1);
        }
    };

    const completeOnboarding = () => {
        localStorage.setItem('onboarding_completed', 'true');
        setIsVisible(false);
        document.body.style.overflow = 'unset';
    };

    if (!isVisible) return null;

    const step = STEPS[currentStep];

    return (
        <div className="onboarding-backdrop">
            <div className="onboarding-card">
                <button className="onboarding-skip" onClick={completeOnboarding}>
                    Skip
                </button>

                <div className="onboarding-content">
                    <div className="onboarding-icon-wrapper">
                        {step.icon}
                    </div>
                    <h2 className="onboarding-title">{step.title}</h2>
                    <p className="onboarding-description">{step.description}</p>
                </div>

                <div className="onboarding-footer">
                    <div className="onboarding-dots">
                        {STEPS.map((_, index) => (
                            <div
                                key={index}
                                className={`onboarding-dot ${index === currentStep ? 'active' : ''}`}
                            />
                        ))}
                    </div>

                    <div className="onboarding-actions">
                        {currentStep > 0 && (
                            <Button variant="secondary" onClick={handleBack}>
                                Back
                            </Button>
                        )}
                        <Button onClick={handleNext}>
                            {currentStep === STEPS.length - 1 ? 'Get Started' : 'Next'}
                        </Button>
                    </div>
                </div>
            </div>
        </div>
    );
}
