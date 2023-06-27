import sklearn
from sklearn.ensemble import RandomForestClassifier

a = sklearn.get_config()
rf = RandomForestClassifier
clf = rf(12, random_state=42)
clf.fit(X, y, sample_weight=weights)

clf_fit = clf.fit
clf_predict = clf.predict

y_pred = clf.predict(X_test)

y_pred = clf.predict(X_test) if foo else clf.fit(X_test)
y_pred = clf_predict(X_test) if False else clf_fit(X_test)