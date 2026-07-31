import cv2
import numpy as np
from typing import Tuple, Optional

from utils.logger import log


class ImageProcessor:
    """
    Classe utilitária para pré-processamento de imagens.
    Contém métodos de conversão, blur, binarização e correção de perspectiva.
    """

    @staticmethod
    def to_grayscale(image: np.ndarray) -> np.ndarray:
        """
        Converte uma imagem BGR para escala de cinza.
        """
        if len(image.shape) == 2:
            return image
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    @staticmethod
    def apply_blur(image: np.ndarray, ksize: Tuple[int, int] = (5, 5)) -> np.ndarray:
        """
        Aplica um filtro Gaussiano para reduzir o ruído (Gaussian Blur).
        """
        return cv2.GaussianBlur(image, ksize, 0)

    @staticmethod
    def apply_threshold(image: np.ndarray, block_size: int = 11, C: int = 2) -> np.ndarray:
        """
        Aplica binarização adaptativa (Adaptive Threshold).
        Excelente para extração de textos em documentos com iluminação irregular.
        """
        if len(image.shape) == 3:
            gray = ImageProcessor.to_grayscale(image)
        else:
            gray = image
            
        return cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, block_size, C
        )

    @staticmethod
    def get_document_contours(image: np.ndarray) -> Optional[np.ndarray]:
        """
        Encontra o maior contorno com 4 vértices (provável documento).
        """
        gray = ImageProcessor.to_grayscale(image)
        blurred = ImageProcessor.apply_blur(gray, (5, 5))
        edged = cv2.Canny(blurred, 75, 200)

        contours, _ = cv2.findContours(edged, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:5]

        for c in contours:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)

            # Se o contorno aproximado tem quatro vértices, assumimos que achamos o documento
            if len(approx) == 4:
                return approx
        
        return None

    @staticmethod
    def order_points(pts: np.ndarray) -> np.ndarray:
        """
        Ordena os 4 pontos do contorno:
        top-left, top-right, bottom-right, bottom-left.
        """
        rect = np.zeros((4, 2), dtype="float32")

        s = pts.sum(axis=1)
        rect[0] = pts[np.argmin(s)]
        rect[2] = pts[np.argmax(s)]

        diff = np.diff(pts, axis=1)
        rect[1] = pts[np.argmin(diff)]
        rect[3] = pts[np.argmax(diff)]

        return rect

    @staticmethod
    def four_point_transform(image: np.ndarray, pts: np.ndarray) -> np.ndarray:
        """
        Aplica uma transformação de perspectiva (bird's eye view).
        """
        rect = ImageProcessor.order_points(pts)
        (tl, tr, br, bl) = rect

        widthA = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
        widthB = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
        maxWidth = max(int(widthA), int(widthB))

        heightA = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
        heightB = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
        maxHeight = max(int(heightA), int(heightB))

        dst = np.array([
            [0, 0],
            [maxWidth - 1, 0],
            [maxWidth - 1, maxHeight - 1],
            [0, maxHeight - 1]
        ], dtype="float32")

        M = cv2.getPerspectiveTransform(rect, dst)
        warped = cv2.warpPerspective(image, M, (maxWidth, maxHeight))

        return warped
        
    @staticmethod
    def fix_perspective(image: np.ndarray) -> np.ndarray:
        """
        Fluxo completo para corrigir a perspectiva do documento, se detectado.
        """
        log.debug("Tentando detectar contorno e corrigir perspectiva do documento.")
        pts = ImageProcessor.get_document_contours(image)
        
        if pts is not None:
            log.debug("Contorno com 4 vértices encontrado. Aplicando transformação.")
            pts = pts.reshape(4, 2)
            return ImageProcessor.four_point_transform(image, pts)
        
        log.warning("Não foi possível encontrar o contorno do documento. Retornando original.")
        return image
