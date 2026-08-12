def calculate_effective_capability(capability_score: float, evidence_confidence: float) -> float:
    """
    Calculates the effective capability score based on the base capability score
    and the confidence in the evidence.
    
    Args:
        capability_score: The raw capability score (0.0 to 1.0).
        evidence_confidence: The confidence in the evidence (0.0 to 1.0).
            - Vendor metadata: 0.40
            - Community benchmark: 0.55
            - AgentHost benchmark: 0.90
            - Current machine test: 0.98
            
    Returns:
        The effective capability score (0.0 to 1.0).
    """
    # Ensure inputs are within the valid range
    score = max(0.0, min(1.0, capability_score))
    confidence = max(0.0, min(1.0, evidence_confidence))
    
    # Strict UNKNOWN penalty: if confidence is <= 0.40 (Vendor claim or Unknown)
    if confidence <= 0.40:
        return score * 0.1 # Heavily penalize to avoid implicit support
        
    return score * confidence
