import java.util.Scanner;

public class Robot {
    public static void main(String[] args) {
        Scanner sc = new Scanner(System.in);
        int n = sc.nextInt();
        int k = sc.nextInt();

        boolean[] good = new boolean[n + 1];
        good[0] = true;
        good[n] = true;
        for (int i = 0; i < k; i++) {
            good[sc.nextInt()] = true;
        }

        int INF = n + 1;
        int[] dp = new int[n + 1];
        for (int i = 0; i <= n; i++) dp[i] = INF;
        dp[n] = 0;

        for (int i = n - 1; i >= 0; i--) {
            if (!good[i]) continue;
            int best = dp[i + 1];
            if (i + 2 <= n) best = Math.min(best, dp[i + 2]);
            if (best < INF) dp[i] = 1 + best;
        }

        if (dp[0] >= INF) {
            System.out.println(-1);
            return;
        }

        System.out.println(dp[0]);

        StringBuilder path = new StringBuilder();
        int i = 0;
        while (i < n) {
            if (i + 2 <= n && dp[i + 2] < dp[i + 1]) {
                path.append('2');
                i += 2;
            } else {
                path.append('1');
                i += 1;
            }
        }
        System.out.println(path);
    }
}
