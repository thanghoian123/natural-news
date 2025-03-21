from app.services.agents import AnalyzingAgent

def get_good_workflow(topic: str):
    # Good workflow
    original_agent = AnalyzingAgent(
        name="OriginalAgent",
        prompt=f"What {topic} is? Where {topic} is commonly found (in which foods, or which products, etc.)."
    )
    benefits_agent = AnalyzingAgent(
        name="BenefitsAgent",
        prompt=f"What are the benefits of {topic}."
    )
    health_benefits_agent = AnalyzingAgent(
        name="HealthBenefitsAgent",
        prompt=f"What are the health benefits of {topic}. Which organ systems does it help?"
    )
    plants_related_agent = AnalyzingAgent(
        name="PlantsRelatedAgent",
        prompt=f"What phytonutrients or phytochemicals does {topic} contain, and what are the primary benefits or uses of those?",
        running_condition=f"Is {topic} a plant-based substance or derived from plants?"
    )
    deficiency_agent = AnalyzingAgent(
        name="DeficiencyAgent",
        prompt=f"What are symptoms of deficiency of {topic}",
    )
    supplementation_agent = AnalyzingAgent(
        name="SupplementationAgent",
        prompt=f"Can {topic} be supplemented? What is the recommended supplementation amount?",
    )
    safety_profile_agent = AnalyzingAgent(
        name="SafetyProfileAgent",
        prompt=f"What is {topic}'s safety profile? Is there a risk of using {topic} too much?",
    )
    public_health_agent = AnalyzingAgent(
        name="PublicHealthAgent",
        prompt=f"How can {topic} contribute to public health and wellness, reduced health care costs and an improved life for people who use it?",
    )

    good_workflow_agents = [
        original_agent,
        benefits_agent,
        health_benefits_agent,
        plants_related_agent,
        deficiency_agent,
        supplementation_agent,
        safety_profile_agent,
        public_health_agent,
    ]

    return good_workflow_agents

def get_bad_workflow(topic: str):
    # Bad workflow
    original_agent = AnalyzingAgent(
        name="OriginalAgent",
        prompt=f"What {topic} is? Where {topic} is commonly found (in which foods, or which products, etc.)."
    )
    harm_effects_agent = AnalyzingAgent(
        name="HarmsEffectsAgent",
        prompt=f"What harms can {topic} cause? What organ systems may be affected? What diseases can {topic} promote?"
    )
    toxicity_agent = AnalyzingAgent(
        name="ToxicityAgent",
        prompt=f"What are symptoms of exposure or toxicity of {topic}?"
    )
    prevention_agent = AnalyzingAgent(
        name="PreventionAgent",
        prompt=f"What natural foods, nutrients, supplements, herbs or essential oils can help protect or detox from {topic}?",
    )
    history_agent = AnalyzingAgent(
        name="HistoryAgent",
        prompt=f"What is the history of {topic}?",
    )
    avoid_strategy_agent = AnalyzingAgent(
        name="AvoidStrategyAgent",
        prompt=f"What are the best strategies for avoiding {topic}?",
    )
    natural_alternative_finding_agents = AnalyzingAgent(
        name="NaturalAlternativeFindingAgents",
        prompt=f"Are there natural alternatives to {topic} that could be used instead?",
    )
    health_cost_agent = AnalyzingAgent(
        name="HealthCostAgent",
        prompt=f"How does {topic} cause increase health care costs due to disease, harm or injury?",
    )

    bad_workflow_agents = [
        original_agent,
        harm_effects_agent,
        toxicity_agent,
        prevention_agent,
        history_agent,
        avoid_strategy_agent,
        natural_alternative_finding_agents,
        health_cost_agent,
    ]

    return bad_workflow_agents