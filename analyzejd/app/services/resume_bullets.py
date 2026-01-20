# app/services/resume_bullets.py
"""
Resume bullet generation for ATS optimization.

Currently uses deterministic templates based on role type.
Will be enhanced with LLM-based personalization in future.
"""


def generate_resume_bullets(jd_text: str) -> list:
    """
    Generate exactly 3 ATS-optimized resume bullets.
    
    Args:
        jd_text: The job description text
        
    Returns:
        List of exactly 3 resume bullets
    """
    jd_lower = jd_text.lower()
    
    # Detect role type for tailored bullets
    is_backend = any(kw in jd_lower for kw in ["backend", "api", "microservices", "database", "sql"])
    is_frontend = any(kw in jd_lower for kw in ["frontend", "react", "angular", "vue", "ui", "ux"])
    is_fullstack = any(kw in jd_lower for kw in ["full stack", "fullstack", "full-stack"])
    is_data = any(kw in jd_lower for kw in ["data", "analytics", "machine learning", "ml", "ai"])
    is_devops = any(kw in jd_lower for kw in ["devops", "cloud", "aws", "azure", "kubernetes", "docker"])
    is_qa = any(kw in jd_lower for kw in ["qa", "quality", "testing", "test automation"])
    
    if is_backend:
        return [
            "Designed and implemented RESTful APIs serving 10K+ requests/day with 99.9% uptime",
            "Optimized database queries reducing average response time by 40% through indexing and query restructuring",
            "Built microservices architecture enabling independent deployment and horizontal scaling"
        ]
    elif is_frontend:
        return [
            "Developed responsive web interfaces using React/Vue achieving 95+ Lighthouse performance scores",
            "Implemented component-based architecture reducing code duplication by 30% across the application",
            "Collaborated with UX team to improve user engagement metrics by 25% through iterative design improvements"
        ]
    elif is_fullstack:
        return [
            "Built end-to-end features from database design to frontend implementation, reducing development cycles by 20%",
            "Integrated third-party APIs and payment gateways handling 1000+ daily transactions securely",
            "Maintained 85% code coverage through comprehensive unit and integration testing"
        ]
    elif is_data:
        return [
            "Developed data pipelines processing 1M+ records daily using Python and SQL for business analytics",
            "Built predictive models achieving 85% accuracy, enabling data-driven decision making",
            "Created interactive dashboards visualizing key metrics for stakeholder reporting"
        ]
    elif is_devops:
        return [
            "Implemented CI/CD pipelines reducing deployment time from hours to minutes with automated testing",
            "Managed cloud infrastructure on AWS/Azure supporting 99.9% application availability",
            "Containerized applications using Docker and Kubernetes for consistent development and production environments"
        ]
    elif is_qa:
        return [
            "Developed automated test suites covering 500+ test cases, reducing regression testing time by 60%",
            "Implemented API testing framework using Postman/RestAssured ensuring 100% endpoint coverage",
            "Collaborated with development team to identify and resolve 200+ bugs before production release"
        ]
    else:
        # Generic software engineering bullets
        return [
            "Developed and maintained scalable software components aligned with product requirements and best practices",
            "Applied problem-solving skills to design efficient algorithms, improving system performance by 25%",
            "Collaborated with cross-functional teams to deliver features on time with comprehensive documentation"
        ]
