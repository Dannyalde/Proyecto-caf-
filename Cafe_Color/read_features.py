import cv2 as cv


class Image:

    def __init__(self,image_path): 
        
        try: 
            self.array_3D = cv.imread(image_path)[...,::-1]
        except ValueError:
            print('Ruta invalida')
        self.properties = self._extract_properties()

    def _extract_properties(self):

        rows, columns, bands = self.array_3D.shape

        properties = {'rows': rows,
                      'columns': columns,
                      'bands': bands,
                      'shape': (rows,columns,bands)}
        
        return properties

