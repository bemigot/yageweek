import java.util.Arrays;

public class ArrSort {
    public static void main(String[] args) {
        int[][] arr24 = {{5, 2, 1, 4}, {9, 6, 5, 8}};

        System.out.println("\nOriginal array: ");
        print2DArray(arr24);

        // Transpose to column-major, sort columns by row-0 value, transpose back
        int[][] t = transpose(arr24);
        // Arrays.sort on a int[][] sorts the outer array's elements — which are the rows.
        Arrays.sort(t, (a, b) -> Integer.compare(a[0], b[0]));

        System.out.println("\nSorted by row 0: ");
        print2DArray(transpose(t));
    }

    public static int[][] transpose(int[][] m) {
        int rows = m.length, cols = m[0].length;
        int[][] t = new int[cols][rows];
        for (int r = 0; r < rows; r++) {
            for (int c = 0; c < cols; c++) {
                t[c][r] = m[r][c];
            }
        }
        return t;
    }

    public static void print2DArray(int[][] array) {
        for (int[] row : array) {
            System.out.println(Arrays.toString(row));
        }
    }
}
// Output:
// Original array:
// [5, 2, 1, 4]
// [9, 6, 5, 8]
// Sorted by row 0:
// [1, 2, 4, 5]
// [5, 6, 8, 9]

/*
   Both Java and default NumPy use row-major convention,
   both store and iterate data row-first:

   Java int[][] — the outer array holds rows; arr[i] gives you row i.
   NumPy (C order) — rows are contiguous in memory; indexing is arr[row, col].
   The column-major restructuring (transposing) makes sort-by-row-vals,
   for it's not Java's native convention.
   NumPy and column-major convention

   NumPy can use Fortran/column-major order (np.array(..., order='F') or
   np.asfortranarray()), but that is opt-in and mainly a memory-layout hint
   for interop with Fortran/BLAS libraries — it does not change the [row, col]
   indexing convention.

   The column-major restructuring / transposing  in Java is purely a workaround
   for Arrays.sort's limitation (it can only sort the outermost dimension).
   NumPy does not have that limitation — argsort + fancy indexing lets you sort
   along any axis directly.

   In NumPy a 2×4 array is stored as two contiguous rows in memory,
   and indexing follows [row, col].

     import numpy as np
     a = np.array([[5, 2, 1, 4],
                   [9, 6, 5, 8]])
     # Sort columns by row-0 values — straightforward:
     idx = np.argsort(a[0])   # [2, 1, 3, 0]
     print(a[:, idx])
     # [[1 2 4 5]
     #  [5 6 8 9]]
 */
