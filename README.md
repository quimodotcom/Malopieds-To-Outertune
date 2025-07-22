# Malopieds To Outertune

This was made to combat a tough yet annoying issue I, and many others, have.

Innertune is an android YouTube Music client which allows for offline music play.

Innertune was not updated to YouTube Music's new API changes and therefore was mostly replaced by various forks. The two for this needed context are Malopieds and Outertune.

Malopieds had various extra features compared to the original Innertune and therefore, a lot of people moved to it. However, Malopieds was not very stable. Plus it didn't have local file integration that most people wanted. This is where Outertune came ontop. It features a lot more stablisation features and the local media functionality that the original Innertune and Malopieds didn't have.

The problem now was backing up your Malopieds backup file and restoring it on Outertune wasn't supported due to the difference in SQLite database table structures.

This script will basically transplant all data from the Malopieds backup, straight to a Outertune backup. 

**Run the main.py, select the Malopieds backup file. The script will then take a empty Outertune backup file and update it with your data. Then transfer the newly updated Outertune backup back to your phone and enjoy!**
