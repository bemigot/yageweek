import java.io.*;
import java.util.*;

public class Select {
    public static void main(String[] args) throws IOException {
        BufferedReader br = new BufferedReader(new InputStreamReader(System.in));
        StringTokenizer st = new StringTokenizer(br.readLine());

        int n = Integer.parseInt(st.nextToken());
        int m = Integer.parseInt(st.nextToken());
        int total = n * m;

        int[][] flat = new int[total][2]; // [value, row]
        int idx = 0;
        for (int r = 0; r < n; r++) {
            st = new StringTokenizer(br.readLine());
            for (int c = 0; c < m; c++) {
                flat[idx][0] = Integer.parseInt(st.nextToken());
                flat[idx][1] = r;
                idx++;
            }
        }

        Arrays.sort(flat, (a, b) -> Integer.compare(a[0], b[0]));

        // nextSameRow[i] = next index in flat with the same row as flat[i]
        int[] nextSameRow = new int[total];
        int[] lastSeen = new int[n];
        Arrays.fill(lastSeen, -1);
        for (int i = total - 1; i >= 0; i--) {
            int r = flat[i][1];
            nextSameRow[i] = lastSeen[r];
            lastSeen[r] = i;
        }

        int[] rowCount = new int[n];
        int[] rowMinIdx = new int[n]; // index in flat of the current min value for each row
        Arrays.fill(rowMinIdx, -1);
        long sum = 0;
        int satisfied = 0;

        long bestRange = Long.MAX_VALUE;
        long bestSum = Long.MAX_VALUE;
        int bestL = 0, bestR = 0;

        int L = 0;
        for (int R = 0; R < total; R++) {
            int r = flat[R][1];
            rowCount[r]++;
            if (rowCount[r] == 1) {
                rowMinIdx[r] = R;
                sum += flat[R][0];
                satisfied++;
            }

            while (satisfied == n) {
                long range = (long) flat[R][0] - flat[L][0];
                if (range < bestRange || (range == bestRange && sum < bestSum)) {
                    bestRange = range;
                    bestSum = sum;
                    bestL = L;
                    bestR = R;
                }

                int lRow = flat[L][1];
                rowCount[lRow]--;
                if (rowCount[lRow] == 0) {
                    sum -= flat[L][0];
                    rowMinIdx[lRow] = -1;
                    satisfied--;
                } else {
                    int newMinIdx = nextSameRow[L];
                    sum += flat[newMinIdx][0] - flat[L][0];
                    rowMinIdx[lRow] = newMinIdx;
                }
                L++;
            }
        }

        // Reconstruct: for each row pick its leftmost (= minimum) element in [bestL, bestR]
        int[] chosen = new int[n];
        boolean[] picked = new boolean[n];
        for (int i = bestL; i <= bestR; i++) {
            int r = flat[i][1];
            if (!picked[r]) {
                chosen[r] = flat[i][0];
                picked[r] = true;
            }
        }

        Arrays.sort(chosen);
        StringBuilder sb = new StringBuilder();
        for (int i = 0; i < n; i++) {
            if (i > 0) sb.append(' ');
            sb.append(chosen[i]);
        }
        System.out.println(sb);
    }
}
