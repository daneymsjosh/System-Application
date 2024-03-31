// Listen for auth status changes, when logged in get data from firestore
auth.onAuthStateChanged((user) => {
  if (user) {
    console.log(user);
    db.collection("Users")
      .doc(user.uid)
      .collection("Classes")
      .onSnapshot(
        (snapshot) => {
          setupClasses(snapshot.docs);
          setupUI(user);
        },
        (err) => {
          console.log(err.message);
        }
      );
  } else {
    setupUI();
    setupClasses([]);
  }
});
