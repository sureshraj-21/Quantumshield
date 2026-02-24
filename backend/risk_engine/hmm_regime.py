import numpy as np
from hmmlearn.hmm import GaussianHMM


def detect_hmm_regime(returns):

    try:
        returns = returns.dropna()

        if len(returns) < 30:
            return "UNKNOWN", 0.0

        # Log returns (more stable)
        X = np.log1p(returns.values).reshape(-1, 1)

        if np.std(X) == 0:
            return "UNKNOWN", 0.0

        # Standardize
        X = (X - X.mean()) / (X.std() + 1e-6)

        model = GaussianHMM(
            n_components=2,
            covariance_type="diag",
            n_iter=300,
            random_state=42
        )

        model.fit(X)
        hidden_states = model.predict(X)

        # Detect high-volatility state as stress
        state_vol = []
        for i in range(2):
            state_data = X[hidden_states == i]
            if len(state_data) == 0:
                state_vol.append(0)
            else:
                state_vol.append(np.std(state_data))

        stress_state = int(np.argmax(state_vol))
        current_state = hidden_states[-1]

        regime = "STRESS" if current_state == stress_state else "CALM"

        probs = model.predict_proba(X)
        stress_probability = float(probs[-1][stress_state])

        return regime, stress_probability

    except Exception:
        return "UNKNOWN", 0.0
